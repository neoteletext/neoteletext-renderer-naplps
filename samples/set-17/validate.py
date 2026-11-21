#!/usr/bin/env python3
"""Build or verify set 17 with the repository renderer and stroke font.

`validate.py --build` regenerates every stream, PNG, the contact sheet and the manifest;
`validate.py` alone checks that each is up to date. Either way each page is generated twice
(it must be byte-identical), checked to be 7-bit, to begin with a full RESET and to define all
sixteen colour-map entries, passed through the renderer's own check, and rendered at
640 x 480 and 480 x 460; a page that WAITs must change between its first stage and the end,
and a page that BLINKs must change with time.
"""
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
FIRST_PAGE, PAGE_COUNT = 217, 10
PAGES = sorted((ROOT / 'pages').glob('[0-9]*.py'))
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'pages'))

from _screen import RESET, DESIGNATE, COLOUR_MAP_SIZE  # noqa: E402

# DOMAIN (0x21), its single-value byte and a four-byte pel size, sent before the colour map.
DOMAIN_LENGTH = 6
# SELECT COLOR (0x3E) and its entry, SET COLOR (0x3C) and a four-byte colour.
PALETTE_ENTRY_LENGTH = 7
SELECT_COLOR, SET_COLOR = 0x3e, 0x3c
OPERAND = 0x40


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
    scanlines = b''.join(b'\0' + rgb[start:start + stride] for start in range(0, len(rgb), stride))
    header = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header)
            + chunk(b'IDAT', zlib.compress(scanlines, 9)) + chunk(b'IEND', b''))


def contact_sheet(images):
    """Pages in two rows of five; within each row the 640 x 480 renders above the 480 x 460, at half size."""
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
    plate = module['build']()
    return plate.stream(), module['META'], len(plate.timeline), getattr(plate, 'blinks', 0)


def verify_stream(stream, name):
    require(stream.isascii(), f'High bit set in {name}')
    require(stream.startswith(RESET + DESIGNATE), f'Missing full reset or designations in {name}')
    start = len(RESET) + len(DESIGNATE) + DOMAIN_LENGTH
    for index in range(COLOUR_MAP_SIZE):
        offset = start + index * PALETTE_ENTRY_LENGTH
        require(stream[offset:offset + 3] == bytes([SELECT_COLOR, OPERAND + index * 4, SET_COLOR])
                and all(value >= OPERAND for value in stream[offset + 3:offset + PALETTE_ENTRY_LENGTH]),
                f'Missing colour-map entry {index} in {name}')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--build', action='store_true', help='write the regenerated deliverables')
    args = parser.parse_args()
    require([int(p.stem[:3]) for p in PAGES] == list(range(FIRST_PAGE, FIRST_PAGE + PAGE_COUNT)),
            f'Expected pages {FIRST_PAGE} to {FIRST_PAGE + PAGE_COUNT - 1}')

    def output(name, data):
        path = OUT / name
        if args.build:
            path.write_bytes(data)
        else:
            require(path.exists() and path.read_bytes() == data, f'Stale output {name}')

    OUT.mkdir(exist_ok=True)
    images, manifest = [], []
    with TemporaryDirectory(dir=ROOT) as temp:
        ppm = Path(temp) / 'page.ppm'
        for script in PAGES:
            stream, meta, waits, blinks = generate(script)
            require(generate(script)[0] == stream, f'Nondeterministic page {script.name}')
            verify_stream(stream, script.name)
            nap = ppm.with_name(script.stem + '.nap')
            nap.write_bytes(stream)
            report = run_renderer('check', '--font', FONT, nap)
            require(report.splitlines()[-1:] == [b'result: clean'], report.decode())
            output(nap.name, stream)
            pair = []
            for width, height in SIZES:
                pixels = raster(nap, ppm, width, height)
                suffix = '' if width == 640 else '-480x460'
                output(f'{script.stem}{suffix}.png', png(width, height, pixels))
                pair.append(pixels)
            notes = []
            if waits:
                require(raster(nap, ppm, 480, 460, '--stage', 1) != pair[1], f'WAIT shows nothing in {nap.name}')
                notes.append(f'{waits} WAITs')
            if blinks:
                phases = {raster(nap, ppm, 480, 460, '--tenths', t) for t in range(0, 40, 3)}
                require(len(phases) > 1, f'BLINK changes nothing in {nap.name}')
                notes.append(f'{blinks} BLINKs')
            require(meta['animated'] == bool(waits or blinks), f'Animated flag wrong in {nap.name}')
            images.append(pair)
            manifest.append(dict(number=int(script.stem[:3]), file=nap.name, title=meta['title'],
                                 purpose=meta['purpose'], style=meta['style'], bytes=len(stream),
                                 techniques=meta['techniques'], animated=meta['animated']))
            print(f'{nap.name} | {len(stream):,} bytes | 7-bit, reset, 16 entries, check clean, '
                  f'both sizes rendered | {", ".join(notes) or "still"}')

    output('manifest.json', (json.dumps(manifest, indent=2) + '\n').encode())
    output('contact-sheet.png', contact_sheet(images))
    print('validate: all pages pass' + (' (deliverables written)' if args.build else ' (deliverables up to date)'))


if __name__ == '__main__':
    main()
