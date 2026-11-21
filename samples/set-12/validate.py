#!/usr/bin/env python3
"""Validate the page and its previews, or rebuild them with --build."""
import argparse
import json
from pathlib import Path
import runpy
import struct
import subprocess
from tempfile import TemporaryDirectory
import zlib

ROOT = Path(__file__).resolve().parent
RENDERER = ROOT.parents[1] / 'target/release/naplps-render'
OUT = ROOT / 'out'
STEM = '176-the-ember-tithe'
SCRIPT = ROOT / 'pages' / f'{STEM}.py'
SIZES = ((640, 480, ''), (480, 460, '-480x460'))


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
        [str(RENDERER), '--width', str(width), '--height', str(height), str(nap), str(ppm)],
        check=True, capture_output=True,
    )
    require(not result.stderr, result.stderr.decode())
    magic, dimensions, maximum, pixels = ppm.read_bytes().split(b'\n', 3)
    require((magic, dimensions, maximum) == (b'P6', f'{width} {height}'.encode(), b'255')
            and len(pixels) == width * height * 3, f'Invalid render at {width} × {height}')
    require(1 < len({pixels[i:i + 3] for i in range(0, len(pixels), 3)}) <= 16,
            f'Unexpected colour count at {width} × {height}')
    return pixels


def contact_sheet(renders):
    gap = 12
    width = sum(w // 2 for w, _, _ in SIZES) + 3 * gap
    height = max(h // 2 for _, h, _ in SIZES) + 2 * gap
    sheet = bytearray(b'\x1e\x22\x3b' * (width * height))
    left = gap
    for (w, h, _), pixels in zip(SIZES, renders):
        top = (height - h // 2) // 2
        for y in range(h // 2):
            source = 2 * y * w * 3
            row = b''.join(pixels[i:i + 3] for i in range(source, source + w * 3, 6))
            dest = ((top + y) * width + left) * 3
            sheet[dest:dest + len(row)] = row
        left += w // 2 + gap
    return png(width, height, sheet)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true', help='regenerate output files')
    args = parser.parse_args()

    page = runpy.run_path(str(SCRIPT))
    stream = page['build']()
    require(stream == runpy.run_path(str(SCRIPT))['build'](), 'Nondeterministic generator')
    require(stream.startswith(b'\x0e\x20\x7f\x7f'), 'Missing initial full RESET')
    require(max(stream) < 128, 'Stream contains non-7-bit bytes')
    start = len(page['SETUP'])
    for index in range(16):
        offset = start + 7 * index
        require(stream[offset:offset + 3] == bytes([0x3e, 0x40 + 4 * index, 0x3c])
                and min(stream[offset + 3:offset + 7]) >= 0x40,
                f'Missing palette definition {index}')

    filename = f'{STEM}.nap'
    manifest = [dict(number=176, file=filename, bytes=len(stream), **page['META'])]
    artifacts = {filename: stream, 'manifest.json': (json.dumps(manifest, indent=2) + '\n').encode()}
    renders = []
    with TemporaryDirectory(dir=ROOT) as temp:
        nap = Path(temp) / filename
        nap.write_bytes(stream)
        check = subprocess.run([str(RENDERER), 'check', str(nap)],
                               check=True, capture_output=True, text=True)
        require(not check.stderr and check.stdout.splitlines()[-1:] == ['result: clean'],
                check.stdout + check.stderr)
        for width, height, suffix in SIZES:
            pixels = render(nap, nap.with_suffix('.ppm'), width, height)
            renders.append(pixels)
            artifacts[f'{STEM}{suffix}.png'] = png(width, height, pixels)

    artifacts['contact-sheet.png'] = contact_sheet(renders)
    OUT.mkdir(exist_ok=True)
    for name, data in artifacts.items():
        path = OUT / name
        if args.build:
            path.write_bytes(data)
        else:
            require(path.is_file() and path.read_bytes() == data, f'Stale output {name}')

    print(f'{STEM} | {len(stream):,} bytes | 640 × 480 and 480 × 460 OK')


if __name__ == '__main__':
    main()
