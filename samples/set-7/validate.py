#!/usr/bin/env python3
"""Regenerate and verify the game screens, or refresh the published set."""
import argparse
import json
import runpy
import struct
import subprocess
import sys
import zlib
from pathlib import Path
from tempfile import TemporaryDirectory

sys.dont_write_bytecode = True
from encoder.screen import RESET, ROOT, SETS

OUT = ROOT / 'out'
REPO = ROOT.parents[1]
RENDERER = REPO / 'target/release/naplps-render'
FONT = REPO / 'fonts/neoteletext.strokes'
SIZES = [(640, 480), (480, 460)]
TIMING = {126: ('--tenths', '6'), 131: ('--stage', '1'),
          133: ('--tenths', '3'), 135: ('--tenths', '4')}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def png(width, height, pixels):
    def chunk(kind, payload):
        return (struct.pack('>I', len(payload)) + kind + payload
                + struct.pack('>I', zlib.crc32(kind + payload)))

    stride = width * 3
    scanlines = b''.join(b'\0' + pixels[i:i+stride] for i in range(0, len(pixels), stride))
    header = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header)
            + chunk(b'IDAT', zlib.compress(scanlines, 9)) + chunk(b'IEND', b''))


def render(page, ppm, width, height, *options):
    result = subprocess.run(
        [str(RENDERER), '--font', str(FONT), '--width', str(width),
         '--height', str(height), *options, str(page), str(ppm)],
        check=True, capture_output=True, text=True)
    require(not result.stderr, result.stderr)
    # The renderer writes a binary Netpbm image with a three-line header.
    magic, dimensions, depth, pixels = ppm.read_bytes().split(b'\n', 3)
    require((magic, dimensions.split(), depth, len(pixels)) ==
            (b'P6', [str(width).encode(), str(height).encode()], b'255', width*height*3),
            f'Unexpected PPM format for {page.name}')
    return pixels


def thumbnail(pixels, width, height):
    # Nearest-neighbour scaling preserves the protocol's hard colour edges.
    rows = []
    for y in range(0, height, 2):
        start = y * width * 3
        row = pixels[start:start + 3*width]
        rows.append(b''.join(row[i:i+3] for i in range(0, len(row), 6)))
    return rows


def contact_sheet(previews):
    gap = 12
    width = 5*320 + 6*gap
    height = 2*(240+230) + 5*gap
    background = b'\x20\x1b\x29'
    pixels = bytearray(background * width * height)
    for index, pair in enumerate(previews):
        for size_index, rows in enumerate(pair):
            tile_width = SIZES[size_index][0]//2
            x = gap + index % 5 * (320 + gap) + (320 - tile_width)//2
            y = gap + index // 5 * (470 + 2*gap) + size_index * (240 + gap)
            for row, data in enumerate(rows):
                start = ((y+row)*width + x)*3
                pixels[start:start+len(data)] = data
    return png(width, height, pixels)


def validate_stream(stream, script):
    require(stream.startswith(RESET + SETS), f'{script.name} lacks the full reset and designations')
    require(all(byte < 128 for byte in stream), f'{script.name} contains non-7-bit data')
    start = len(RESET + SETS) + 6  # Skip the initial DOMAIN.
    for index in range(16):
        entry = stream[start + 7*index:start + 7*(index+1)]
        require(len(entry) == 7 and entry[:3] == bytes([0x3e, 0x40 + 4*index, 0x3c])
                and min(entry[3:]) >= 0x40, f'{script.name} lacks palette entry {index}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', help='refresh streams, PNGs and manifest')
    args = parser.parse_args()
    scripts = sorted((ROOT / 'pages').glob('[0-9]*.py'))
    require([int(script.name[:3]) for script in scripts] == list(range(126, 136)),
            'Expected exactly pages 126 through 135')
    manifest = []
    previews = []

    def publish(name, data):
        path = OUT / name
        if args.build:
            path.write_bytes(data)
        else:
            require(path.read_bytes() == data, f'Stale output {name}')

    with TemporaryDirectory(dir=ROOT) as temp:
        ppm = Path(temp) / 'screen.ppm'
        for script in scripts:
            source = runpy.run_path(str(script))
            stream = source['build']().stream()
            second = runpy.run_path(str(script))
            require((stream, source['META']) == (second['build']().stream(), second['META']),
                    f'{script.name} is nondeterministic')
            validate_stream(stream, script)
            number = int(script.name[:3])
            page = ppm.with_name(script.stem + '.nap')
            page.write_bytes(stream)
            report = subprocess.run(
                [str(RENDERER), 'check', '--font', str(FONT), str(page)],
                check=True, capture_output=True, text=True)
            require(report.stdout.splitlines()[-1:] == ['result: clean'] and not report.stderr,
                    report.stdout + report.stderr)
            meta = source['META']
            require(meta['animated'] == (number in TIMING), f'Unexpected timing for {script.name}')
            manifest.append(dict(number=number, file=page.name, title=meta['title'],
                                 purpose=meta['purpose'], style=meta['style'], bytes=len(stream),
                                 techniques=meta['techniques'], animated=meta['animated']))
            publish(page.name, stream)
            previews.append([])
            for width, height in SIZES:
                pixels = render(page, ppm, width, height)
                if number in TIMING:
                    require(pixels != render(page, ppm, width, height, *TIMING[number]),
                            f'{script.name} timing made no visible change')
                suffix = '' if width == 640 else f'-{width}x{height}'
                publish(script.stem + suffix + '.png', png(width, height, pixels))
                previews[-1].append(thumbnail(pixels, width, height))
            print(f'{page.name} | {len(stream):,} bytes | 640 × 480 and 480 × 460 OK')
    publish('manifest.json', (json.dumps(manifest, indent=2) + '\n').encode())
    publish('contact-sheet.png', contact_sheet(previews))


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT / 'pages'))
    main()
