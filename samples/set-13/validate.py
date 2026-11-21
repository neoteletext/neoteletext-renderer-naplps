#!/usr/bin/env python3
"""Validate every page in pages/, or rebuild the outputs with --build.

Each page is generated twice and must be identical, must be 7-bit, must begin with a full
RESET and must define the sixteen colour-map entries in order. Each stream is checked by
the renderer, then rendered at 640 by 480 and at 480 by 460 (the channel's size).
"""
import argparse
import json
from pathlib import Path
import re
import runpy
import struct
import subprocess
import sys
from tempfile import TemporaryDirectory
import zlib

ROOT = Path(__file__).resolve().parent
PAGES = ROOT / 'pages'
OUT = ROOT / 'out'
RENDERER = ROOT.parents[1] / 'target/release/naplps-render'
FONT = ROOT.parents[1] / 'fonts/neoteletext.strokes'
RESET = b'\x0e\x20\x7f\x7f'
SIZES = ((640, 480, ''), (480, 460, '-480x460'))
COLOUR_MAP_ENTRIES = 16
PAGE_NAME = re.compile(r'^(\d{3})-([a-z0-9-]+)\.py$')

sys.path.insert(0, str(PAGES))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def png(width, height, pixels):
    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data
                + struct.pack('>I', zlib.crc32(kind + data)))

    stride = 3 * width
    rows = b''.join(b'\0' + pixels[i:i + stride] for i in range(0, len(pixels), stride))
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows))
            + chunk(b'IEND', b''))


def render(nap, ppm, width, height):
    result = subprocess.run(
        [str(RENDERER), '--width', str(width), '--height', str(height), '--font', str(FONT), str(nap), str(ppm)],
        check=True, capture_output=True,
    )
    require(not result.stderr, result.stderr.decode())
    magic, dimensions, maximum, pixels = ppm.read_bytes().split(b'\n', 3)
    require((magic, dimensions, maximum) == (b'P6', f'{width} {height}'.encode(), b'255')
            and len(pixels) == width * height * 3, f'Invalid render at {width} x {height}')
    colours = len({pixels[i:i + 3] for i in range(0, len(pixels), 3)})
    require(1 < colours <= COLOUR_MAP_ENTRIES, f'Unexpected colour count {colours} at {width} x {height}')
    return pixels


def contact_sheet(rows):
    """Half-size renders, one row of pages per pair of rows: the 640 by 480 row, then the 480 by 460 row."""
    gap = 12
    cell_w = max(w for w, _, _ in SIZES) // 2
    cell_h = max(h for _, h, _ in SIZES) // 2
    per_row = 5
    blocks = [rows[i:i + per_row] for i in range(0, len(rows), per_row)]
    width = per_row * cell_w + (per_row + 1) * gap
    height = len(blocks) * (2 * cell_h + 3 * gap) + gap
    sheet = bytearray(b'\x1e\x22\x3b' * (width * height))
    top = gap
    for block in blocks:
        for size_index, (w_full, h_full, _) in enumerate(SIZES):
            for column, (renders) in enumerate(block):
                pixels = renders[size_index]
                left = gap + column * (cell_w + gap)
                w, h = w_full, h_full
                for y in range(h // 2):
                    source = 2 * y * w * 3
                    row = b''.join(pixels[i:i + 3] for i in range(source, source + w * 3, 6))
                    dest = ((top + y) * width + left) * 3
                    sheet[dest:dest + len(row)] = row
            top += cell_h + gap
        top += gap
    return png(width, height, sheet)


def load(path):
    """Import a page script without running its __main__ block, and return its build function and META."""
    namespace = runpy.run_path(str(path), run_name='set13_page')
    return namespace['build'], namespace['META']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', help='write the output files')
    args = parser.parse_args()

    scripts = sorted(p for p in PAGES.iterdir() if PAGE_NAME.match(p.name))
    require(len(scripts) == 10, f'Expected ten pages, found {len(scripts)}')
    artifacts = {}
    manifest = []
    renders_by_page = []
    for script in scripts:
        stem = script.stem
        number = int(PAGE_NAME.match(script.name).group(1))
        build, meta = load(script)
        stream = build().stream()
        require(stream == build().stream(), f'{stem}: nondeterministic generator')
        require(stream.startswith(RESET), f'{stem}: missing initial full RESET')
        require(max(stream) < 128, f'{stem}: stream contains non-7-bit bytes')
        position = 0
        for index in range(COLOUR_MAP_ENTRIES):
            pattern = bytes([0x3e, 0x40 + 4 * index, 0x3c])
            found = stream.find(pattern, position)
            require(found >= 0, f'{stem}: missing colour-map entry {index}')
            position = found + len(pattern)
        filename = f'{stem}.nap'
        manifest.append(dict(number=number, file=filename, bytes=len(stream), **meta))
        artifacts[filename] = stream

        renders = []
        with TemporaryDirectory() as temp:
            nap = Path(temp) / filename
            nap.write_bytes(stream)
            check = subprocess.run([str(RENDERER), 'check', '--font', str(FONT), str(nap)],
                                   check=True, capture_output=True, text=True)
            require(not check.stderr and check.stdout.splitlines()[-1:] == ['result: clean'],
                    f'{stem}: ' + check.stdout + check.stderr)
            for width, height, suffix in SIZES:
                pixels = render(nap, nap.with_suffix('.ppm'), width, height)
                renders.append(pixels)
                artifacts[f'{stem}{suffix}.png'] = png(width, height, pixels)
        renders_by_page.append(renders)
        print(f'{stem} | {len(stream):,} bytes | 640 x 480 and 480 x 460 OK')

    artifacts['contact-sheet.png'] = contact_sheet(renders_by_page)
    artifacts['manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    OUT.mkdir(exist_ok=True)
    for name, data in artifacts.items():
        path = OUT / name
        if args.build:
            path.write_bytes(data)
        else:
            require(path.is_file() and path.read_bytes() == data, f'Stale output {name}')
    print(f'{len(scripts)} pages validated' + (' and written' if args.build else ''))


if __name__ == '__main__':
    main()
