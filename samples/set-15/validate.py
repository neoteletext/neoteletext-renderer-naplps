#!/usr/bin/env python3
"""Build or verify set 15 with the repository renderer and stroke font.

Without arguments: regenerate every stream twice, check it is deterministic, 7-bit, begins with a full
RESET and defines all sixteen colour-map entries; run the renderer's check; render it at 640 x 480 and
480 x 460; check its animation changes the picture; and compare everything with the saved outputs.
With --build: write the streams, PNGs, contact sheet and manifest instead of comparing.
"""
import argparse
import json
import os
import runpy
import struct
import subprocess
import sys
import zlib
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'out'
REPO = ROOT.parents[1]
RENDERER = REPO / 'target/release/naplps-render'
FONT = REPO / 'fonts/neoteletext.strokes'
SIZES = ((640, 480), (480, 460))
FIRST, LAST = 197, 206
PAGES = sorted((ROOT / 'pages').glob('[0-9]*.py'))
SCRATCH = Path(os.environ.get('TMPDIR', Path.home() / '.cache' / 'cft'))
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'pages'))

from encoder import RESET, DESIGNATE  # noqa: E402


def require(condition, description):
    if not condition:
        raise ValueError(description)


def run_renderer(*args):
    result = subprocess.run([str(RENDERER), *map(str, args)], capture_output=True)
    require(result.returncode == 0 and not result.stderr,
            f'renderer failed: {result.stderr.decode()} {result.stdout.decode()}')
    return result.stdout


def raster(nap, ppm, width, height, *options):
    run_renderer('--font', FONT, '--width', width, '--height', height, *options, nap, ppm)
    magic, size, maximum, pixels = ppm.read_bytes().split(b'\n', 3)
    require(magic == b'P6' and list(map(int, size.split())) == [width, height]
            and maximum == b'255' and len(pixels) == width * height * 3,
            f'invalid raster for {nap.name}')
    return pixels


def png(width, height, rgb):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))

    stride = width * 3
    scanlines = b''.join(b'\0' + rgb[start:start + stride] for start in range(0, len(rgb), stride))
    header = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header)
            + chunk(b'IDAT', zlib.compress(scanlines, 9)) + chunk(b'IEND', b''))


def contact_sheet(images):
    """Two groups of five: 640 x 480 renders above 480 x 460 renders, each at half size."""
    gap, cell_width = 12, 320
    width = 5 * cell_width + 6 * gap
    height = 2 * sum(h // 2 for _, h in SIZES) + 5 * gap
    rgb = bytearray(b'\x22\x24\x2b' * (width * height))
    top = gap
    for group in (images[:5], images[5:]):
        for size_index, (w, h) in enumerate(SIZES):
            for column, pair in enumerate(group):
                left = gap + column * (cell_width + gap) + (cell_width - w // 2) // 2
                for y in range(h // 2):
                    start = 2 * y * w * 3
                    row = bytearray(w // 2 * 3)
                    source = pair[size_index][start:start + w * 3]
                    for channel in range(3):
                        row[channel::3] = source[channel::6]
                    dest = ((top + y) * width + left) * 3
                    rgb[dest:dest + len(row)] = row
            top += h // 2 + gap
    return png(width, height, rgb)


def generate(script):
    module = runpy.run_path(str(script))
    return module['build']().stream(), module['META']


def verify_stream(stream, name):
    require(stream.startswith(RESET + DESIGNATE), f'{name} does not begin with a full RESET')
    require(all(byte < 0x80 for byte in stream), f'{name} has a byte with the high bit set')
    start = len(RESET + DESIGNATE) + 6  # after the DOMAIN that sets the pel
    for index in range(16):
        offset = start + index * 7
        require(stream[offset:offset + 3] == bytes([0x3e, 0x40 + index * 4, 0x3c])
                and all(value >= 0x40 for value in stream[offset + 3:offset + 7]),
                f'{name} does not define colour-map entry {index}')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--build', action='store_true', help='write the regenerated deliverables')
    args = parser.parse_args()
    require([int(p.stem[:3]) for p in PAGES] == list(range(FIRST, LAST + 1)), f'expected pages {FIRST} to {LAST}')

    def output(name, data):
        path = OUT / name
        if args.build:
            path.write_bytes(data)
        else:
            require(path.exists() and path.read_bytes() == data, f'stale output {name}')

    OUT.mkdir(exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    images, manifest = [], []
    with TemporaryDirectory(dir=SCRATCH) as temp:
        ppm = Path(temp) / 'page.ppm'
        for script in PAGES:
            stream, meta = generate(script)
            require(generate(script) == (stream, meta), f'nondeterministic page {script.name}')
            verify_stream(stream, script.name)
            nap = ppm.with_name(script.stem + '.nap')
            nap.write_bytes(stream)
            report = run_renderer('check', '--font', FONT, nap)
            require(report.splitlines()[-1:] == [b'result: clean'], report.decode())
            output(nap.name, stream)
            pair = []
            for width, height in SIZES:
                pixels = raster(nap, ppm, width, height)
                colours = {pixels[i:i + 3] for i in range(0, len(pixels), 3)}
                require(1 < len(colours) <= 16, f'unexpected rendered colour count in {nap.name}')
                suffix = '' if width == 640 else '-480x460'
                output(f'{script.stem}{suffix}.png', png(width, height, pixels))
                pair.append(pixels)
            if meta['animated']:
                staged = raster(nap, ppm, 480, 460, '--stage', 1) != pair[1]
                blinking = raster(nap, ppm, 480, 460, '--tenths', 3) != raster(nap, ppm, 480, 460, '--tenths', 8)
                require(staged or blinking, f'{nap.name} is marked animated but neither WAIT nor BLINK changes it')
                motion = ', '.join(m for m, on in (('WAIT', staged), ('BLINK', blinking)) if on)
            else:
                motion = 'static'
            images.append(pair)
            manifest.append(dict(number=int(script.stem[:3]), file=nap.name, title=meta['title'],
                                 purpose=meta['purpose'], style=meta['style'], bytes=len(stream),
                                 techniques=meta['techniques'], animated=meta['animated']))
            print(f'{nap.name} | {len(stream):,} bytes | 7-bit, RESET, 16 colours, check clean | '
                  f'640x480 and 480x460 OK | {motion}')

    output('manifest.json', (json.dumps(manifest, indent=2) + '\n').encode())
    output('contact-sheet.png', contact_sheet(images))
    print('all pages', 'built' if args.build else 'verified')


if __name__ == '__main__':
    main()
