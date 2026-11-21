#!/usr/bin/env python3
"""Regenerate and check the ten pages of set 16.

Without options it regenerates every stream, checks that generation is
deterministic and that the stream is 7-bit, begins with a full reset and
defines all sixteen colours, renders it at 640 by 480 and 480 by 460 with the
repository's renderer, and compares everything with the files in out/.
--build writes those files instead of comparing.  --snapshot R also copies
the renders into rounds/round-R/.
"""
import argparse
import json
import os
import runpy
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
REPOSITORY = HERE.parents[1]
RENDERER = REPOSITORY / 'target' / 'release' / 'naplps-render'
FONT = REPOSITORY / 'fonts' / 'neoteletext.strokes'
SCRATCH = Path.home() / '.cache' / 'cft'
FIRST_PAGE, LAST_PAGE = 207, 216
SIZES = ((640, 480, ''), (480, 460, '-480x460'))
RESET = b'\x0e\x20\x7f\x7f'
SELECT_COLOR, SET_COLOR = 0x3e, 0x3c
SHEET_COLUMNS, SHEET_GAP, SHEET_GROUND = 5, 10, b'\x18\x1a\x20'

sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE / 'pages'))


class Fault(Exception):
    """A page or an output that fails a check."""


def generate(script):
    module = runpy.run_path(str(script))
    return module['build']().stream(), module['META']


def check_stream(stream, name):
    if not stream.startswith(RESET):
        raise Fault(f'{name}: does not begin with a full reset')
    if any(byte > 0x7f for byte in stream):
        raise Fault(f'{name}: not 7-bit')
    defined = set()
    for offset in range(len(stream) - 2):
        if stream[offset] == SELECT_COLOR and stream[offset + 2] == SET_COLOR:
            defined.add((stream[offset + 1] & 0x3f) >> 2)
    if defined != set(range(16)):
        raise Fault(f'{name}: colour map entries not defined: {sorted(set(range(16)) - defined)}')


def renderer(*arguments):
    done = subprocess.run([str(RENDERER), *map(str, arguments)], capture_output=True)
    if done.returncode or done.stderr:
        raise Fault(f'renderer failed on {arguments[-2:]}: {done.stderr.decode().strip()}')
    return done.stdout.decode()


def render(stream_file, width, height, scratch):
    picture = scratch / 'page.ppm'
    renderer('--font', FONT, '--width', width, '--height', height, stream_file, picture)
    magic, size, depth, pixels = picture.read_bytes().split(b'\n', 3)
    if magic != b'P6' or size.split() != [str(width).encode(), str(height).encode()] \
            or depth != b'255' or len(pixels) != width * height * 3:
        raise Fault(f'{stream_file.name}: bad picture at {width} by {height}')
    return pixels


def png(width, height, pixels):
    def chunk(kind, body):
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))

    row = width * 3
    lines = b''.join(b'\x00' + pixels[at:at + row] for at in range(0, len(pixels), row))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(lines, 9)) + chunk(b'IEND', b''))


def halve(width, height, pixels):
    """Every second pixel of every second row."""
    rows = []
    for y in range(0, height - 1, 2):
        line = pixels[y * width * 3:(y + 1) * width * 3]
        half = bytearray(width // 2 * 3)
        for channel in range(3):
            half[channel::3] = line[channel::6]
        rows.append(bytes(half))
    return width // 2, len(rows), rows


def contact_sheet(renders):
    """Two rows of five pages; each page's 640 by 480 above its 480 by 460, at half size."""
    cell = SIZES[0][0] // 2
    tall = [size[1] // 2 for size in SIZES]
    block = sum(tall) + SHEET_GAP
    width = SHEET_COLUMNS * cell + (SHEET_COLUMNS + 1) * SHEET_GAP
    bands = (len(renders) + SHEET_COLUMNS - 1) // SHEET_COLUMNS
    height = bands * (block + 2 * SHEET_GAP) + SHEET_GAP
    sheet = bytearray(SHEET_GROUND * (width * height))
    for index, pair in enumerate(renders):
        left = SHEET_GAP + (index % SHEET_COLUMNS) * (cell + SHEET_GAP)
        top = SHEET_GAP + (index // SHEET_COLUMNS) * (block + 2 * SHEET_GAP)
        for (full_width, full_height, _), pixels in zip(SIZES, pair):
            small_width, small_height, rows = halve(full_width, full_height, pixels)
            inset = left + (cell - small_width) // 2
            for y, line in enumerate(rows):
                at = ((top + y) * width + inset) * 3
                sheet[at:at + len(line)] = line
            top += small_height + SHEET_GAP
    return png(width, height, bytes(sheet))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--build', action='store_true', help='write out/ instead of comparing with it')
    parser.add_argument('--snapshot', type=int, metavar='R', help='with --build: copy the renders to rounds/round-R/')
    parser.add_argument('--only', type=int, metavar='NNN', help='with --build: one page, no sheet or manifest')
    options = parser.parse_args()

    scripts = sorted((HERE / 'pages').glob('[0-9][0-9][0-9]-*.py'))
    numbers = [int(script.name[:3]) for script in scripts]
    if not options.only and numbers != list(range(FIRST_PAGE, LAST_PAGE + 1)):
        raise Fault(f'expected pages {FIRST_PAGE} to {LAST_PAGE}, found {numbers}')
    if options.only:
        scripts = [script for script in scripts if int(script.name[:3]) == options.only]

    stale = []

    def deliver(name, content):
        target = OUT / name
        if options.build:
            target.write_bytes(content)
        elif not target.exists() or target.read_bytes() != content:
            stale.append(name)

    SCRATCH.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(exist_ok=True)
    os.environ['TMPDIR'] = str(SCRATCH)
    renders, manifest, total = [], [], 0
    with tempfile.TemporaryDirectory(dir=SCRATCH) as folder:
        scratch = Path(folder)
        for script in scripts:
            stream, meta = generate(script)
            again, _ = generate(script)
            if again != stream:
                raise Fault(f'{script.name}: two runs gave different streams')
            check_stream(stream, script.name)
            stream_file = scratch / (script.stem + '.nap')
            stream_file.write_bytes(stream)
            report = renderer('check', '--font', FONT, stream_file).strip().splitlines()
            if report[-1] != 'result: clean':
                raise Fault(f'{script.name}: renderer check says {report[-1]}')
            deliver(stream_file.name, stream)
            pair = []
            for width, height, suffix in SIZES:
                pixels = render(stream_file, width, height, scratch)
                deliver(f'{script.stem}{suffix}.png', png(width, height, pixels))
                pair.append(pixels)
            renders.append(pair)
            manifest.append({'number': int(script.name[:3]), 'file': stream_file.name,
                             'title': meta['title'], 'purpose': meta['purpose'], 'style': meta['style'],
                             'bytes': len(stream), 'techniques': meta['techniques'],
                             'animated': meta['animated']})
            total += len(stream)
            print(f'{stream_file.name}: {len(stream):,} bytes, deterministic, 7-bit, '
                  f'renders at 640x480 and 480x460')

    if not options.only:
        deliver('manifest.json', (json.dumps(manifest, indent=2) + '\n').encode())
        deliver('contact-sheet.png', contact_sheet(renders))
    if stale:
        raise Fault('out/ does not match the generators: ' + ', '.join(stale))
    if options.build and options.snapshot is not None:
        keep = HERE / 'rounds' / f'round-{options.snapshot}'
        keep.mkdir(parents=True, exist_ok=True)
        for picture in sorted(OUT.glob('*.png')):
            shutil.copy2(picture, keep / picture.name)
        print(f'renders copied to rounds/round-{options.snapshot}/')
    print(f'{len(scripts)} pages, {total:,} bytes: '
          + ('written' if options.build else 'all checks passed, out/ is current'))


if __name__ == '__main__':
    try:
        main()
    except Fault as fault:
        sys.exit(f'FAILED: {fault}')
