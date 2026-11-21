"""Regenerate and validate the samples, previews and manifest."""
import argparse
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import zlib

sys.dont_write_bytecode = True

from encoder import RESET, ROOT, SETS

OUT = ROOT / 'out'
REPO = ROOT.parent.parent
SIZES = ((640, 480), (480, 460))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(command):
    result = subprocess.run(command, capture_output=True, check=True)
    require(not result.stderr, f'{command}: {result.stderr.decode(errors="replace")}')
    return result.stdout


def render(renderer, font, source, temp, width, height, phase=None):
    command = [renderer, '--font', font, '--width', str(width), '--height', str(height)]
    if phase is not None:
        command.extend(('--tenths', str(phase)))
    run([*command, source, temp])
    magic, dimensions, depth, pixels = temp.read_bytes().split(b'\n', 3)
    require((magic, dimensions, depth) == (b'P6', f'{width} {height}'.encode(), b'255')
            and len(pixels) == width * height * 3, f'{source.name}: invalid PPM')
    colors = {pixels[i:i+3] for i in range(0, len(pixels), 3)}
    require(1 < len(colors) <= 16, f'{source.name}: unexpected rendered palette')
    return pixels


def write_png(path, width, height, pixels):
    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data
                + struct.pack('>I', zlib.crc32(kind + data)))

    stride = width * 3
    scanlines = b''.join(b'\0' + pixels[i:i+stride] for i in range(0, len(pixels), stride))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'
                     + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(scanlines, 9))
                     + chunk(b'IEND', b''))


def contact_sheet(previews):
    width, height = 5 * 320 + 6 * 12, 2 * 240 + 3 * 12
    sheet = bytearray(bytes((225, 220, 210)) * width * height)
    for index, pixels in enumerate(previews):
        x = 12 + (index % 5) * 332
        y = 12 + (index // 5) * 252
        for row in range(240):
            origin = row * 2 * 640 * 3
            line = pixels[origin:origin + 640 * 3]
            reduced = b''.join(line[column:column+3] for column in range(0, len(line), 6))
            start = ((y+row) * width + x) * 3
            sheet[start:start+960] = reduced
    write_png(OUT / 'contact-sheet.png', width, height, sheet)


def validate(renderer, font):
    scripts = sorted((ROOT / 'pages').glob('[0-9]*.py'))
    numbers = [int(path.name.split('-')[0]) for path in scripts]
    require(numbers == list(range(156, 166)), f'Unexpected page numbers: {numbers}')
    OUT.mkdir(exist_ok=True)
    manifest = []
    previews = []

    with tempfile.TemporaryDirectory(prefix='validate-', dir=ROOT) as directory:
        temp = Path(directory) / 'preview.ppm'
        for number, script in zip(numbers, scripts):
            source = OUT / (script.stem + '.nap')
            spec = importlib.util.spec_from_file_location(script.stem, script)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            run([sys.executable, '-B', script])
            stream = source.read_bytes()
            run([sys.executable, '-B', script])
            require(stream == source.read_bytes(), f'{script.name}: nondeterministic stream')
            require(stream.isascii(), f'{source.name}: 7-bit violation')
            require(stream.startswith(RESET + SETS), f'{source.name}: missing initial reset or set designations')
            palette = stream[len(RESET + SETS) + 6:][:112]
            for index in range(16):
                entry = palette[index*7:(index+1)*7]
                require(entry[:3] == bytes((0x3e, 64 + index*4, 0x3c))
                        and len(entry) == 7 and all(64 <= b <= 127 for b in entry[3:]),
                        f'{source.name}: invalid palette entry {index}')
            diagnostics = run([renderer, 'check', '--font', font, source])
            require(b'result: clean' in diagnostics, diagnostics.decode())
            meta = module.META
            for width, height in SIZES:
                pixels = render(renderer, font, source, temp, width, height)
                suffix = '' if width == 640 else f'-{width}x{height}'
                write_png(OUT / f'{script.stem}{suffix}.png', width, height, pixels)
                if width == 640:
                    previews.append(pixels)
                if meta['animated']:
                    alternate = render(renderer, font, source, temp, width, height, 10)
                    require(alternate != pixels, f'{source.name}: BLINK phase has no visible effect')
            manifest.append(dict(number=number, file=source.name, title=meta['title'],
                                 purpose=meta['purpose'], style=meta['style'], bytes=len(stream),
                                 techniques=meta['techniques'], animated=meta['animated']))
            print(f'{number} {meta["title"]}: {len(stream)} bytes, both sizes clean', flush=True)
    contact_sheet(previews)
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renderer', type=Path, default=REPO / 'target/release/naplps-render')
    parser.add_argument('--font', type=Path, default=REPO / 'fonts/neoteletext.strokes')
    args = parser.parse_args()
    validate(args.renderer.resolve(), args.font.resolve())
