#!/usr/bin/env python3
"""Publish the local manifest, design notes and protocol-derived animation previews."""
from pathlib import Path
from PIL import Image
import json,re,subprocess,tempfile
from catalog import PAGES
from render import ROOT,RENDER,FONT

def picture(data,tenths=0):
    with tempfile.TemporaryDirectory(dir=ROOT/'out') as tmp:
        nap=Path(tmp)/'stage.nap';ppm=Path(tmp)/'stage.ppm';nap.write_bytes(data)
        result=subprocess.run([str(RENDER),'--font',str(FONT),'--tenths',str(tenths),str(nap),str(ppm)],capture_output=True,text=True,check=True)
        if result.stderr.strip():raise RuntimeError(result.stderr)
        with Image.open(ppm) as im:return im.convert('RGB').copy()

def animations():
    orbit=(ROOT/'out/098-orbit-status.nap').read_bytes()
    frames=[picture(orbit,t) for t in [0,2]]
    for f,name in zip(frames,['dim','lit']):f.save(ROOT/f'out/098-orbit-status-blink-{name}.png')
    frames[0].save(ROOT/'out/098-orbit-status.gif',save_all=True,append_images=frames[1:],duration=[200,1400],loop=0)
    lottery=(ROOT/'out/104-lottery-results.nap').read_bytes()
    boundaries=list(re.finditer(re.escape(b'\x3d\x5c')+b'[\x40-\x7f]',lottery))
    stages=[picture(lottery[:m.start()]) for m in boundaries]+[picture(lottery)]
    for i,f in enumerate(stages):f.save(ROOT/f'out/104-lottery-results-stage-{i:02d}.png')
    stages[0].save(ROOT/'out/104-lottery-results.gif',save_all=True,append_images=stages[1:],duration=[300]*len(boundaries)+[1500],loop=0)

manifest=[];summary=[]
for number,slug,title,purpose,style,techniques,animated,note in PAGES:
    name=f'{number:03d}-{slug}';nap=ROOT/'out'/f'{name}.nap'
    manifest.append(dict(number=number,file=nap.name,title=title,purpose=purpose,style=style,bytes=nap.stat().st_size,techniques=techniques,animated=animated))
    summary.append(f'{number:03d} | {title} | {purpose} | {nap.stat().st_size:,} bytes'+(' | animated' if animated else ' | still'))
(ROOT/'out/manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
intro='''# Twenty-five independent NAPLPS services / 086–110

[640-pixel contact sheet](out/contact-sheet.png) · [Native 256-pixel contact sheet](out/contact-sheet-256.png) · [Manifest](out/manifest.json) · [Validation report](out/validation.json)

These are separate fictional services, not a branded collection. Their colour families, geometry, density, borders and composition follow the individual purposes in CONCEPTS.txt. Each numbered Python generator is independently runnable from any directory and writes its matching stream into `out/`. The encoder and page generators use only the Python standard library; Pillow is used solely by the preview and checking scripts. All artwork is native NAPLPS geometry, characters, patterns or macros, with Microstar as the only stroke font. No external artwork, assets or brands are used.

Reproduce from this directory:

```sh
python3 render.py      # generate 25 streams, 100 still previews and two contact sheets
python3 finish.py      # manifest, these notes, summary and two protocol-derived GIFs
python3 validate.py    # deterministic output, sizes, reset independence and content checks
```

For a single page, use `python3 pages/093-ski-report.py`, then `python3 render.py 093`. Full-size images have the same stem as the stream. Smaller previews have `-256x200`, `-320x200` and `-512x400` suffixes. The 5 × 5 main contact sheet uses 320 × 240 thumbnails of the 640 × 480 renders; the small contact sheet pastes actual 256 × 200 renders without resampling.

## Encoding and review

Every stream first designates G1 as PDI (`1B 29 57`) so even a predecessor that reassigned G1 cannot intercept its reset, then immediately sends `SO RESET 7F 7F` (`0E 20 7F 7F`). G0 primary, G2 macros and G3 mosaics are explicitly designated after reset. Every page defines all sixteen colour-map entries, uses one-byte single operands and four-byte coordinate/colour operands (`DOMAIN 21 4C`), and sets a nonzero logical pel. The extended local `pages/lib.py` reuses the supplied encoder but suppresses redundant state commands, measures proportional stroke extents, and enforces the stricter 6,144-byte ceiling. All streams are 7-bit and all are below 3 KB. No word-wrap, cursor, input-field or transmit-macro facility is used.

Every final page was inspected at 640 × 480 and at native 256 × 200. The 320 × 200 and 512 × 400 previews were also generated. The visual iterations included heavier crossword rules, thicker branched DRCS snowflakes, a shorter ticket seat line, a corrected tide ordinate and an accurately sized dinosaur/human comparison. Main copy generally uses fields of at least 20 design pixels (1/32 screen width); smaller diagram indices and nonessential security detail are secondary. Static pictures remain complete with either phase of the mission LED.

`validate.py` regenerates every stream to check determinism, checks manifest counts, seven-bit data, reset and all sixteen palette definitions, dimensions and palette counts at all four sizes. It compares each page after a different predecessor at both 640 and 256 widths, then repeats at 256 after deliberately hostile character-set assignments. It also verifies the actual mate-in-two, crossword interlock, 60-seat allocation, WAIT budget and LED phases. The machine-readable report includes SHA-256 hashes and exact byte sizes.

## Timing and renderer observations

Only **098** and **104** are animated. Kestrel blinks a small LED using `3F 5C 42 4E 40` on selected entry 8: entry 7 for two tenths, entry 8 for fourteen. Lucky Comet has seven `3D 5C 43` WAITs, totalling 21 tenths (2.1 seconds), and settles on a complete result screen. Its final `SELECT COLOR 7; SET COLOR` redefines already drawn confetti. All other pages have neither WAIT nor BLINK. Both are below the brief’s eight-page animation allowance.

The known **WAIT preview limitation** is present: `naplps-render` feeds the entire stream and does not stop at WAIT. Thus the seven `3D 5C 43` commands in 104 do not delay the CLI’s final PNG. `finish.py` renders stream prefixes at the exact WAIT boundaries for the numbered stage PNGs and GIF; the GIF adds a final viewing hold and loops for review, whereas NAPLPS plays once and holds. The mission GIF samples the native BLINK states with `--tenths 0` and `--tenths 2`. [Mission GIF](out/098-orbit-status.gif) · [Lottery GIF](out/104-lottery-results.gif).

A suspected **rotated-glyph edge clipping/rounding issue** was observed on the queen’s lower Q: at x=496 a glyph stroke on its rotated field boundary disappeared, while x=490 retained it at all four output sizes. The failing TEXT/POINT/character bytes were `22 42 40 40 4A 6A 56 24 58 44 72 5D 0F 51 0E`; the workaround aligns the origin to a common pixel boundary, using POINT `24 58 44 62 45` instead. These operands are derived from the generator’s four-byte encoding; no renderer code was changed. Apart from this visual observation, no malformed-stream errors or processing-limit warnings were observed. Known period differences in very large/rotated stroke type, downloadable character rasterisation and separated-mosaic spacing still apply; these previews are not PP3 oracle certifications. The queen’s lower Q deliberately uses a half-turn; ellipse shapes that are not circular are explicitly faceted polygons rather than unsupported multi-point spline arcs. Fine decorative banknote engraving is allowed to merge at low resolution while its labels stay legible. Nothing outside this working directory was changed in the project.

## Pages

'''
paragraphs=[]
for row,m in zip(PAGES,manifest):
    number,slug,title,purpose,style,techniques,animated,note=row
    stem=f'{number:03d}-{slug}'
    paragraphs.append(f'### {number:03d} — {title}\n\n[Preview](out/{stem}.png) · [256 × 200](out/{stem}-256x200.png) · [Stream](out/{stem}.nap) · **{m["bytes"]:,} bytes**\n\n{note}\n')
(ROOT/'DESIGN.md').write_text(intro+'\n'.join(paragraphs))
animations()
notes='Renderer: WAIT does not pause CLI previews; rotated Q edge clipping was avoided with an aligned origin (bytes and workaround in DESIGN.md). All 25 final pictures are complete stills.'
(ROOT/'out/summary.txt').write_text('\n'.join(summary+[notes])+'\n')
print('\n'.join(summary+[notes]))
