#!/usr/bin/env python3
"""Validate reproducibility, stream framing, native renders and timing."""
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.dont_write_bytecode = True
from render import (FONT, OUT, PAGES, RENDERER, ROOT, SIZES,
                    generate, preview_path, render, write_png)
from _support import RESET

MANIFEST_FIELDS = {'number', 'file', 'title', 'purpose', 'style', 'bytes',
                   'techniques', 'animated'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_stream(script, manifest_entry, page, ppm):
    stream, meta = generate(script)
    require(generate(script) == (stream, meta), f'{script.name} is nondeterministic')
    expected = dict(number=int(script.stem[:3]), file=page.name, bytes=len(stream), **meta)
    require(set(expected) == MANIFEST_FIELDS and expected == manifest_entry,
            f'Manifest disagrees with {script.name}')
    require(stream == (OUT / page.name).read_bytes(), f'Stale stream for {script.name}')
    require(stream.startswith(RESET) and max(stream) < 128,
            f'Invalid reset or 8-bit data in {script.name}')
    # After the four character-set designations and the six-byte DOMAIN,
    # each map definition is SELECT, SET COLOR and four RGB operand bytes.
    start = len(RESET) + 12 + 6
    for index in range(16):
        offset = start + 7 * index
        require(stream[offset:offset + 3] == bytes([0x3e, 0x40 + 4 * index, 0x3c])
                and min(stream[offset + 3:offset + 7]) >= 0x40,
                f'Missing colour-map entry {index} in {script.name}')

    page.write_bytes(stream)
    report = subprocess.run([str(RENDERER), 'check', '--font', str(FONT), str(page)],
                            check=True, capture_output=True, text=True)
    require(report.stdout.splitlines()[-1:] == ['result: clean'] and not report.stderr,
            f'{script.name}: {report.stdout}{report.stderr}')
    for width, height in SIZES:
        pixels = render(page, ppm, width, height)
        colour_count = len({pixels[i:i + 3] for i in range(0, len(pixels), 3)})
        require(1 < colour_count <= 16, f'Unexpected colour count for {script.name}')
        candidate = ppm.with_suffix('.png')
        write_png(candidate, width, height, pixels)
        require(candidate.read_bytes() == preview_path(script, width, height).read_bytes(),
                f'Stale preview for {script.name} at {width} × {height}')


def validate_timing(page, ppm):
    def image(*options):
        return render(page, ppm, 480, 460, *options)

    if page.name.startswith('121-'):
        phases = [image('--tenths', t) for t in range(16, 28, 2)]
        require(len(set(phases)) == 6 and phases[0] == image('--tenths', 28),
                'Afterimage must show six distinct phases and repeat')
    elif page.name.startswith('122-'):
        stages = [image('--stage', n) for n in (1, 2, 0)]
        require(len(set(stages)) == 3, 'The Lure must have three distinct stages')


def main():
    manifest = json.loads((OUT / 'manifest.json').read_text())
    require([int(p.stem[:3]) for p in PAGES] == list(range(121, 126))
            and len(manifest) == len(PAGES), 'Expected exactly pages 121–125')
    with TemporaryDirectory(dir=ROOT) as temp:
        ppm = Path(temp) / 'page.ppm'
        for script, entry in zip(PAGES, manifest):
            nap = ppm.with_name(script.stem + '.nap')
            validate_stream(script, entry, nap, ppm)
            validate_timing(nap, ppm)
            print(f'{script.stem} | 640 × 480 and 480 × 460 OK')
    print('All five pages passed. The six BLINK phases and three WAIT stages are distinct.')


if __name__ == '__main__':
    main()
