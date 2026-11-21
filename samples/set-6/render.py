#!/usr/bin/env python3
"""Generate streams, native-size previews and a two-size contact sheet."""
import json
import runpy
import struct
import subprocess
import sys
import zlib
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
OUT = ROOT / 'out'
RENDERER = REPO / 'target/release/naplps-render'
FONT = REPO / 'fonts/neoteletext.strokes'
SIZES = [(640, 480), (480, 460)]
PAGES = sorted((ROOT / 'pages').glob('[0-9]*.py'))
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'pages'))


def generate(script):
    module = runpy.run_path(str(script))
    return module['build']().stream(), module['META']


def render(page, ppm, width, height, *options):
    result = subprocess.run(
        [str(RENDERER), '--font', str(FONT), '--width', str(width),
         '--height', str(height), *map(str, options), str(page), str(ppm)],
        check=True, capture_output=True,
    )
    if result.stderr:
        raise RuntimeError(result.stderr.decode())
    magic, dimensions, maximum, pixels = ppm.read_bytes().split(b'\n', 3)
    if (magic, dimensions.split(), maximum, len(pixels)) != (
        b'P6', [str(width).encode(), str(height).encode()], b'255', width * height * 3
    ):
        raise ValueError(f'Unexpected PPM header or data length in {ppm}')
    return pixels


def write_png(path, width, height, pixels):
    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data
                + struct.pack('>I', zlib.crc32(kind + data)))

    rows = (b'\0' + pixels[i:i + 3 * width] for i in range(0, len(pixels), 3 * width))
    path.write_bytes(
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
        + chunk(b'IDAT', zlib.compress(b''.join(rows)))
        + chunk(b'IEND', b'')
    )


def preview_path(script, width, height):
    suffix = '' if width == 640 else f'-{width}x{height}'
    return OUT / f'{script.stem}{suffix}.png'


def contact_sheet(images):
    gap, cell_w = 12, 320
    width = (cell_w + gap) * len(images) + gap
    height = sum(h // 2 for _, h in SIZES) + gap * (len(SIZES) + 1)
    sheet = bytearray(b'\x1b\x1d\x24' * (width * height))
    top = gap
    for size_index, (w, h) in enumerate(SIZES):
        for i, pair in enumerate(images):
            pixels = pair[size_index]
            left = gap + i * (cell_w + gap) + (cell_w - w // 2) // 2
            for y in range(h // 2):
                start = (2 * y) * w * 3
                source = pixels[start:start + w * 3]
                row = bytes(component for x in range(0, len(source), 6)
                            for component in source[x:x + 3])
                dest = ((top + y) * width + left) * 3
                sheet[dest:dest + len(row)] = row
        top += h // 2 + gap
    write_png(OUT / 'contact-sheet.png', width, height, sheet)


def main():
    OUT.mkdir(exist_ok=True)
    images, manifest = [], []
    with TemporaryDirectory(dir=ROOT) as temp:
        ppm = Path(temp) / 'page.ppm'
        for script in PAGES:
            stream, meta = generate(script)
            nap = OUT / (script.stem + '.nap')
            nap.write_bytes(stream)
            manifest.append(dict(number=int(script.stem[:3]), file=nap.name,
                                 title=meta['title'], purpose=meta['purpose'], style=meta['style'],
                                 bytes=len(stream), techniques=meta['techniques'],
                                 animated=meta['animated']))
            pair = []
            for width, height in SIZES:
                pixels = render(nap, ppm, width, height)
                write_png(preview_path(script, width, height), width, height, pixels)
                pair.append(pixels)
            images.append(pair)
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    contact_sheet(images)


if __name__ == '__main__':
    main()
