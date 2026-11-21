#!/usr/bin/env python3
"""Check the sample artifacts. Use --build to regenerate them."""
import argparse
import json
from pathlib import Path
import runpy
import struct
import subprocess
import sys
from tempfile import TemporaryDirectory
import zlib

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
OUT = ROOT / 'out'
RENDERER = REPO / 'target/release/naplps-render'
FONT = REPO / 'fonts/neoteletext.strokes'
SIZES = ((640, 480), (480, 460))
FIELDS = {'number', 'file', 'title', 'purpose', 'style', 'bytes', 'techniques', 'animated'}

sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'pages'))
from _canvas import RESET, SETS


def require(condition, message):
    if not condition:
        raise ValueError(message)


def generate(script):
    page = runpy.run_path(str(script))
    return page['build']().stream(), page['META']


def check_stream(name, stream):
    require(stream.startswith(RESET + SETS), f'{name}: missing reset or designations')
    require(stream.isascii(), f'{name}: 8-bit data')
    palette_start = len(RESET + SETS) + 6  # Initial four-coordinate-byte DOMAIN
    for i in range(16):
        offset = palette_start + 7 * i
        expected = bytes((0x3e, 0x40 + 4 * i, 0x3c))
        require(stream[offset:offset + 3] == expected
                and len(stream[offset + 3:offset + 7]) == 4
                and all(b >= 0x40 for b in stream[offset + 3:offset + 7]),
                f'{name}: missing palette entry {i}')


def run(*args):
    result = subprocess.run([RENDERER, *map(str, args)], capture_output=True, check=True)
    require(not result.stderr, result.stderr.decode())
    return result.stdout


def render(nap, ppm, width, height, *options):
    run('--font', FONT, '--width', width, '--height', height, *options, nap, ppm)
    magic, dimensions, maximum, pixels = ppm.read_bytes().split(b'\n', 3)
    require(magic == b'P6' and dimensions.split() == [str(width).encode(), str(height).encode()]
            and maximum == b'255' and len(pixels) == width * height * 3,
            f'{nap.name}: invalid {width} × {height} PPM')
    colours = {pixels[i:i + 3] for i in range(0, len(pixels), 3)}
    require(1 < len(colours) <= 16, f'{nap.name}: unexpected colour count')
    return pixels


def png(width, height, pixels):
    def chunk(kind, payload):
        crc = zlib.crc32(kind + payload)
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', crc)

    stride = width * 3
    rows = b''.join(b'\0' + pixels[i:i + stride] for i in range(0, len(pixels), stride))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


def contact_sheet(images):
    gap, tile_width, tile_height = 10, 240, 230
    width = 5 * tile_width + 6 * gap
    height = 2 * tile_height + 3 * gap
    sheet = bytearray(b'\x1a\x18\x24' * width * height)
    for i, pixels in enumerate(images):
        x = gap + (i % 5) * (tile_width + gap)
        y = gap + (i // 5) * (tile_height + gap)
        for row in range(tile_height):
            source = row * 2 * 480 * 3
            line = b''.join(pixels[j:j + 3] for j in range(source, source + 480 * 3, 6))
            dest = ((y + row) * width + x) * 3
            sheet[dest:dest + len(line)] = line
    return png(width, height, sheet)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', help='write streams, previews and manifest')
    build = parser.parse_args().build
    scripts = sorted((ROOT / 'pages').glob('[0-9]*.py'))
    require([s.stem[:3] for s in scripts] == [str(n) for n in range(146, 156)],
            'Expected exactly pages 146–155')

    def artifact(name, data):
        path = OUT / name
        if build:
            path.write_bytes(data)
        else:
            require(path.exists() and path.read_bytes() == data, f'{name}: missing or stale')

    if build:
        OUT.mkdir(exist_ok=True)
    manifest, images = [], []
    with TemporaryDirectory(dir=ROOT) as directory:
        ppm = Path(directory) / 'page.ppm'
        for script in scripts:
            stream, meta = generate(script)
            require(generate(script) == (stream, meta), f'{script.name}: nondeterministic generation')
            nap = ppm.with_name(script.stem + '.nap')
            check_stream(nap.name, stream)
            nap.write_bytes(stream)
            report = run('check', '--font', FONT, nap)
            require(report.splitlines()[-1:] == [b'result: clean'], report.decode())
            entry = dict(number=int(script.stem[:3]), file=nap.name, bytes=len(stream), **meta)
            require(entry.keys() == FIELDS, f'{script.name}: invalid manifest fields')
            manifest.append(entry)
            artifact(nap.name, stream)
            for width, height in SIZES:
                pixels = render(nap, ppm, width, height)
                suffix = '' if width == 640 else '-480x460'
                artifact(script.stem + suffix + '.png', png(width, height, pixels))
            images.append(pixels)
            if entry['number'] == 148:
                require(pixels != render(nap, ppm, 480, 460, '--tenths', 6),
                        'Final Spin: BLINK has no visible alternate phase')
            if entry['number'] == 151:
                require(pixels != render(nap, ppm, 480, 460, '--stage', 1),
                        'Kiln Opening: WAIT has no visible opening stage')
            print(f'{nap.name} | {len(stream):,} bytes | 640 × 480 and 480 × 460 OK')
    artifact('manifest.json', (json.dumps(manifest, indent=2) + '\n').encode())
    artifact('contact-sheet.png', contact_sheet(images))


if __name__ == '__main__':
    main()
