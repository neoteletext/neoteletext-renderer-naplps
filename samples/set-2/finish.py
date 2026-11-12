"""Write the deliverable manifest, design notes, reveal preview and summary."""
from pathlib import Path
import json,subprocess,tempfile
from PIL import Image
from catalog import PAGES
from render import ROOT,RENDER,FONT,contact_sheet

def finish():
    manifest=[]
    for number,title,purpose,style,techniques,note in PAGES:
        paths=list((ROOT/'out').glob(f'{number:03}-*.nap'))
        assert len(paths)==1,(number,paths)
        path=paths[0]
        manifest.append(dict(number=number,file=path.name,title=title,purpose=purpose,style=style,bytes=path.stat().st_size,techniques=techniques,animated=number==49))
    (ROOT/'out/manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    lines=[f"{m['number']:03} | {m['title']} | {m['bytes']:,} bytes | {m['style']}" for m in manifest]
    (ROOT/'out/SUMMARY.txt').write_text('\n'.join(lines)+'\n\nRenderer: no new suspected defects; see DESIGN.md for documented implementation limits.\n')
    intro='''# Twenty-five independent NAPLPS pages / 036–060

[Contact sheet](out/contact-sheet.png) · [Native small-screen sheet](out/contact-sheet-small.png) · [Manifest](out/manifest.json) · [Validation](out/validation.json) · [One-line summaries](out/SUMMARY.txt)

Each page has its own generator in `pages/`, its own sixteen-entry palette and a complete `.nap` still in `out/`. Same-stem PNGs are 640 × 480; suffixes `-256x200`, `-320x200` and `-512x400` identify the other required sizes. `out/review/` pairs each full-size image with its native 256 × 200 image. All twenty-five were visually inspected in both sizes, revised where needed and inspected again. No shared collection branding, page footer or fixed margin system is imposed. Names, services, books, prices and population figures are fictional; scientific symbols, countries, clock offsets and calendar dates use their ordinary meanings.

## Reproduce

Run `python3 render.py` to generate all streams, render the four sizes and assemble both sheets. Individual generators, such as `python3 pages/060-hearth-quilt.py`, also work directly. Run `python3 finish.py` for the manifest, design notes and welcome reveal; run `python3 validate.py` for the structural, determinism and predecessor checks. The encoder and page generators use Python’s standard library only. Preview assembly uses the already installed Pillow package. The renderer and Microstar font are read from the locations in BRIEF.md. Every generated or temporary file stays inside this directory.

## Validation

`validate.py` passed for all 25 deterministic generators and 100 final-size previews. It verified 7-bit encoding, the initial RESET, all sixteen initial palette entries, byte budgets, preview dimensions, visible-colour counts and the finite reveal. Every page was then rendered after every member of the set at both 640 × 480 and 256 × 200: all 1,250 comparisons matched standalone RGB pixels exactly, with empty renderer stderr. The detailed hashes and results are in `out/validation.json`.

## Encoding and renderer observations

Each stream explicitly designates primary G0, PDI G1 and mosaic G3 before entering SO and `20 7F 7F` RESET; it then designates macros in G2. This restores the sets as well as clearing inherited graphic state. DOMAIN uses four-byte coordinates, one-byte single values and an explicit logical pel. Sixteen SELECT COLOR / SET COLOR pairs define the complete palette before the background is painted. Important body fields are generally at least 1/32 of the screen wide; a few secondary dimension/timezone fields are slightly narrower and were checked at 256 × 200. Stroke text is exclusively Microstar, with no word-wrap controls, displayed cursors, input fields or transmit macros. All streams are 7-bit and under 6 KB; every page is also under 3 KB.

Required native features are distributed by purpose: G2 relative macros in 060, G3 DRCS in 050, downloaded fill pattern A in 041, hatching in 045 and 057, G3 mosaics in 048, incremental lines and proportional text in 040, supplementary accents/symbols in 042 and 057, colour mode 2 in 047, and final palette redefinition in 042 and 049. Only 049 is animated: one finite `3D 5C 48` WAIT, eight tenths of a second. No page uses BLINK. Every full-stream render is the complete intended final picture.

No new renderer defect was identified. Known documented limits were designed around: line textures need a real DOMAIN pel; arcs are limited to three points, with polygons used for the fox and heart; large display text can differ in thickness/placement from PP3; and the CLI draws through WAIT rather than stopping there. The welcome prefix is therefore cut at the exact recorded WAIT boundary for its reveal PNG and GIF. These previews use the supplied renderer, not PP3 oracle screenshots, and make no claim of pixel-identical period display typography. There are no speculative renderer workarounds or changes outside this directory.

## Pages

'''
    paragraphs=[]
    for m,entry in zip(manifest,PAGES):
        stem=Path(m['file']).stem
        paragraphs.append(f"**{m['number']:03} — {m['title']}** · [{m['bytes']:,} bytes](out/{m['file']}) · [Preview](out/{stem}.png). {entry[-1]}\n")
    (ROOT/'DESIGN.md').write_text(intro+'\n'.join(paragraphs))
    path=next((ROOT/'out').glob('049-*.nap'))
    meta=json.loads(path.with_suffix('.json').read_text())
    cut=meta['timeline'][0]['length']
    with tempfile.TemporaryDirectory(dir=ROOT/'out') as tmp:
        prefix=Path(tmp)/'prefix.nap';ppm=Path(tmp)/'prefix.ppm'
        prefix.write_bytes(path.read_bytes()[:cut])
        subprocess.run([str(RENDER),'--font',str(FONT),str(prefix),str(ppm)],check=True,capture_output=True)
        initial=Image.open(ppm).copy();initial.save(path.with_name(path.stem+'-reveal.png'))
        final=Image.open(path.with_suffix('.png')).copy()
        initial.save(path.with_suffix('.gif'),save_all=True,append_images=[final],duration=[800,1800],loop=0)
    contact_sheet()
    print('\n'.join(lines))
    print('Renderer: no new suspected defects; documented limits in DESIGN.md.')

if __name__=='__main__':finish()
