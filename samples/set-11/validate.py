#!/usr/bin/env python3
"""Build or verify the set with the repository renderer and stroke font."""
import argparse
import json
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
PAGES = sorted((ROOT / 'pages').glob('[0-9]*.py'))
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'pages'))

from _drawing import RESET


def require(condition, description):
    if not condition:
        raise ValueError(description)


def run_renderer(*args):
    result = subprocess.run([str(RENDERER), *map(str, args)], check=True, capture_output=True)
    require(not result.stderr, result.stderr.decode())
    return result.stdout


def raster(nap, ppm, width, height, *options):
    run_renderer('--font', FONT, '--width', width, '--height', height, *options, nap, ppm)
    magic, size, maximum, pixels = ppm.read_bytes().split(b'\n', 3)
    require(magic == b'P6' and list(map(int, size.split())) == [width, height]
            and maximum == b'255' and len(pixels) == width * height * 3,
            f'Invalid raster for {nap.name}')
    return pixels


def png(width, height, rgb):
    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data
                + struct.pack('>I', zlib.crc32(kind + data)))

    stride = width * 3
    scanlines = b''.join(b'\0' + rgb[start:start + stride]
                         for start in range(0, len(rgb), stride))
    header = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header)
            + chunk(b'IDAT', zlib.compress(scanlines)) + chunk(b'IEND', b''))


def contact_sheet(images):
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
    require(stream.startswith(RESET) and stream.isascii(),
            f'Invalid reset or high bit in {name}')
    start = len(RESET) + 12 + 6
    for index in range(16):
        offset = start + index * 7
        require(stream[offset:offset + 3] == bytes([0x3e, 0x40 + index * 4, 0x3c])
                and all(value >= 0x40 for value in stream[offset + 3:offset + 7]),
                f'Missing palette definition {index} in {name}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', help='write the regenerated deliverables')
    args = parser.parse_args()
    require([int(p.stem[:3]) for p in PAGES] == list(range(166, 176)), 'Expected pages 166–175')

    def output(name, data):
        path = OUT / name
        if args.build:
            path.write_bytes(data)
        else:
            require(path.read_bytes() == data, f'Stale output {name}')

    images, manifest = [], []
    with TemporaryDirectory(dir=ROOT) as temp:
        ppm = Path(temp) / 'page.ppm'
        for script in PAGES:
            stream, meta = generate(script)
            require(generate(script) == (stream, meta), f'Nondeterministic page {script.name}')
            verify_stream(stream, script.name)
            nap = ppm.with_name(script.stem + '.nap')
            nap.write_bytes(stream)
            report = run_renderer('check', '--font', FONT, nap)
            require(report.splitlines()[-1:] == [b'result: clean'], report.decode())
            output(nap.name, stream)
            pair = []
            for width, height in SIZES:
                pixels = raster(nap, ppm, width, height)
                require(1 < len({pixels[i:i+3] for i in range(0, len(pixels), 3)}) <= 16,
                        f'Unexpected rendered colour count in {nap.name}')
                suffix = '' if width == 640 else '-480x460'
                output(f'{script.stem}{suffix}.png', png(width, height, pixels))
                pair.append(pixels)
            if script.stem.startswith('170-'):
                phases = [raster(nap, ppm, 480, 460, '--tenths', t) for t in (0, 4, 11)]
                require(phases[0] != phases[1] and phases[0] == phases[2], 'BLINK failed')
            if script.stem.startswith('171-'):
                require(raster(nap, ppm, 480, 460, '--stage', 1) != pair[1], 'WAIT failed')
            images.append(pair)
            manifest.append(dict(number=int(script.stem[:3]), file=nap.name, bytes=len(stream), **meta))
            print(f'{nap.name} | {len(stream):,} bytes | both sizes OK')

    output('manifest.json', (json.dumps(manifest, indent=2) + '\n').encode())
    output('contact-sheet.png', contact_sheet(images))


if __name__ == '__main__':
    main()
