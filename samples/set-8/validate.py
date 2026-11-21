#!/usr/bin/env python3
"""Regenerate, verify and render the set. Use --write to update deliverables."""
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
OUT = ROOT / 'out'
REPO = ROOT.parents[1]
RENDERER = REPO / 'target/release/naplps-render'
FONT = REPO / 'fonts/neoteletext.strokes'
SIZES = ((640, 480), (480, 460))
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'pages'))
from _drawing import RESET, SETUP


def build(script):
    module = runpy.run_path(str(script))
    return module['build']().stream(), module['META']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_stream(stream, name):
    require(stream.isascii(), f'{name} contains high-bit bytes')
    prefix = RESET + SETUP
    require(stream.startswith(prefix), f'{name} lacks the full reset and setup')
    domain = stream[len(prefix):len(prefix)+6]
    require(domain.startswith(b'!L'), f'{name} lacks a four-byte DOMAIN')
    palette = stream[len(prefix)+6:]
    for index in range(16):
        entry = palette[index*7:index*7+7]
        require(entry.startswith(bytes((0x3e, 0x40+index*4, 0x3c)))
                and len(entry) == 7 and all(0x40 <= b < 0x80 for b in entry[3:]),
                f'{name} has a malformed colour-map entry {index}')


def render(nap, ppm, width, height):
    result = subprocess.run([str(RENDERER), '--font', str(FONT),
                             '--width', str(width), '--height', str(height),
                             str(nap), str(ppm)], capture_output=True, check=True)
    require(not result.stderr, result.stderr.decode(errors='replace'))
    magic, dimensions, maximum, pixels = ppm.read_bytes().split(b'\n', 3)
    require(magic == b'P6' and dimensions == f'{width} {height}'.encode()
            and maximum == b'255' and len(pixels) == width*height*3,
            f'Bad PPM for {nap.name}')
    return pixels


def png(width, height, pixels):
    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data
                + struct.pack('>I', zlib.crc32(kind + data)))

    pitch = width*3
    rows = b''.join(b'\0'+pixels[i:i+pitch] for i in range(0,len(pixels),pitch))
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB',width,height,8,2,0,0,0))
            + chunk(b'IDAT',zlib.compress(rows)) + chunk(b'IEND',b''))


def update(path, data, write):
    if write:
        path.write_bytes(data)
    else:
        require(path.read_bytes() == data, f'{path.name} differs from regeneration')


def contact_sheet(pages):
    # Paired rows within each group of five. Nearest-neighbour reduction
    # keeps palette entries and crisp edges intact.
    gap, cell, columns = 10, 320, 5
    width = columns*cell+(columns+1)*gap
    height = 2*sum(h//2 for _,h in SIZES)+5*gap
    sheet = bytearray(b'\x18\x19\x21'*(width*height))
    top = gap
    for offset in (0,5):
        for index,(w,h) in enumerate(SIZES):
            for col, pair in enumerate(pages[offset:offset+5]):
                left = gap+col*(cell+gap)+(cell-w//2)//2
                for y in range(h//2):
                    start = 2*y*w*3
                    source = pair[index][start:start+w*3]
                    row = b''.join(source[x:x+3] for x in range(0,len(source),6))
                    dest = ((top+y)*width+left)*3
                    sheet[dest:dest+len(row)] = row
            top += h//2+gap
    return png(width,height,sheet)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    write = parser.parse_args().write
    scripts = sorted((ROOT/'pages').glob('[0-9]*.py'))
    require([int(s.stem[:3]) for s in scripts] == list(range(136,146)),
            'Expected exactly pages 136 through 145')
    images, manifest = [], []
    with TemporaryDirectory(dir=ROOT) as temp:
        scratch = Path(temp)
        for script in scripts:
            stream, meta = build(script)
            require((stream, meta) == build(script), f'{script.name} is nondeterministic')
            check_stream(stream, script.name)
            nap = scratch / (script.stem+'.nap')
            nap.write_bytes(stream)
            update(OUT/nap.name, stream, write)
            manifest.append(dict(number=int(script.stem[:3]), file=nap.name, **meta))
            manifest[-1]['bytes'] = len(stream)
            pair = []
            for width, height in SIZES:
                pixels = render(nap, scratch/'preview.ppm', width, height)
                suffix = '' if width == 640 else f'-{width}x{height}'
                update(OUT/f'{script.stem}{suffix}.png', png(width,height,pixels), write)
                pair.append(pixels)
            images.append(pair)
            print(f'{nap.name}  {len(stream):4} bytes  640×480 and 480×460')
    update(OUT/'manifest.json', (json.dumps(manifest, indent=2, ensure_ascii=False)+'\n').encode(), write)
    update(OUT/'contact-sheet.png', contact_sheet(images), write)


if __name__ == '__main__':
    main()
