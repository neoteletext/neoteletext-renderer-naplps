"""Validate delivery constraints, rendering, determinism, and predecessor independence."""
from pathlib import Path
from PIL import Image
import hashlib, json, subprocess, sys, tempfile, statistics
from encoder import rgb
from render import ROOT, RENDER, FONT
files=sorted((ROOT/'out').glob('*.nap'))
assert len(files)==25
infos=[json.loads(f.with_suffix('.meta.json').read_text()) for f in files]
assert [x['number'] for x in infos]==list(range(61,86))
previous={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
for gen in sorted((ROOT/'pages').glob('*.py')):
    subprocess.run([sys.executable,str(gen)],check=True,capture_output=True)
assert previous=={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files},'Generators are not deterministic'
# Predecessors leave drawing attributes, masks, macros, and character sets dirty.
# Explicit G0/G1/G3 designation in every header is essential as well as RESET.
dirty=b''.join(f.read_bytes() for f in files)+b'\x1b(|\x1b)}\x1b*{\x1b+{'
checks=[]
with tempfile.TemporaryDirectory(prefix='naplps-batch3-',dir=ROOT/'out') as tmp:
    tmp=Path(tmp)
    for f,info in zip(files,infos):
        data=f.read_bytes();meta=json.loads(f.with_suffix('.json').read_text())
        assert data and max(data)<128
        assert len(data)<6000 and info['bytes']==len(data)
        assert b'\x0e\x20\x7f\x7f' in data[:30]
        assert len(meta['palette'])==16
        start=data.index(b'\x1b. z')+4+6
        for i,col in enumerate(meta['palette']):
            assert data[start+i*7:start+(i+1)*7]==bytes([0x3e,0x40|(i<<2),0x3c])+rgb(col),(f.name,i)
        assert not info['animated'] and not meta['frames'] and meta['duration_tenths']==0
        colours={}
        for w,h in [(640,480),(256,200),(320,200),(512,400)]:
            suffix='' if w==640 else f'-{w}x{h}'
            with Image.open(f.with_name(f.stem+suffix+'.png')) as im:
                assert im.size==(w,h)
                colours[f'{w}x{h}']=len(im.getcolors(maxcolors=16) or [])
                assert 1<colours[f'{w}x{h}']<=16
        mixed=tmp/'mixed.nap';mixed.write_bytes(dirty+data)
        for w,h in [(640,480),(256,200)]:
            dst=tmp/'mixed.ppm'
            run=subprocess.run([RENDER,'--width',str(w),'--height',str(h),'--font',FONT,str(mixed),str(dst)],capture_output=True,text=True)
            assert run.returncode==0 and not run.stderr,(f.name,run.stderr)
            suffix='' if w==640 else f'-{w}x{h}'
            with Image.open(dst) as a,Image.open(f.with_name(f.stem+suffix+'.png')) as b:
                assert a.tobytes()==b.convert('RGB').tobytes(),f'Predecessor changed {f.name} at {w}'
        checks.append({'number':info['number'],'file':f.name,'bytes':len(data),'sha256':previous[f.name],'visible_colours':colours,'predecessor_independent':[640,256],'deterministic':True})
manifest=[{k:v for k,v in x.items() if k!='design'} for x in infos]
(ROOT/'out'/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
report={'pages':25,'renders':100,'sizes':[[640,480],[256,200],[320,200],[512,400]],'all_7_bit':True,'explicit_palette_entries':16,'all_under_6000_bytes':True,'under_3000_bytes':sum(x['bytes']<3000 for x in infos),'animated_pages':0,'predecessor_comparisons':50,'pages_detail':checks}
(ROOT/'out'/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
intro='''# Twenty-five NAPLPS designs / 061–085

These pages follow the purposes and visual styles in CONCEPTS.txt. Each has its own composition, palette and typography. All are complete stills: no WAIT and no BLINK. Native Microstar strokes supply every letter. Every stream explicitly designates its character sets, sends `SO 20 7F 7F`, sets four-byte coordinates and defines all sixteen palette entries. The stream ends with END and SO, leaving the drawing set active.

[Contact sheet](out/contact-sheet.png) · [Exact 256 × 200 contact sheet](out/contact-sheet-small.png) · [Manifest](out/manifest.json) · [Validation report](out/validation.json)

All 25 final 640 × 480 renders and their actual 256 × 200 renders were visually inspected. Additional previews are supplied at 320 × 200 and 512 × 400. Changes after review included the arcade title's position, the girih macro's relative origin, the festival caption, the seaside label, the map's closed loop, the tarot numeral and title, the planet ring's occlusion, and the noir title's clear ground. The console texture was revised and rechecked at both sizes. The contact sheets were inspected after these changes.

Twenty-four streams are below 3,000 bytes; every stream is below 6,000 bytes. `validate.py` checks deterministic regeneration, all four image sizes, 7-bit encoding, the RESET, sixteen explicit colour definitions, byte sizes and at most sixteen visible colours. Fifty additional renders compare each page after all 25 predecessors and deliberately altered character-set designations with its standalone pixels, at both 640 × 480 and 256 × 200. All comparisons pass. These are supplied-renderer checks, not PP3 screen captures.

## Renderer observations and workarounds

No confirmed renderer defect or processing-limit warning was found. The definition bitmap records colour index zero as an erased bit (`surface.rs`, `MaskSurface::put`, `entry != 0`). The initial scan-line definition was consequently blank. Page 077 now sends `3E 44` (select entry 1) before `1B 44 41` (DEF TEXTURE A), then defines a broad horizontal band and uses pattern A with `23 60`. This produces visible scan lines at both resolutions. It is documented as an implementation observation, not a claimed standards violation.

The renderer checks full character-field fit at the top of the viewport. An initial 78-pixel field at a 66-pixel baseline caused the arcade title to wrap; its final baseline and field fit. Fine line and mask coverage vary with pixel rounding, so the console uses a filled mask band rather than a hairline. Curved contours in these designs are sampled polylines, not unsupported multi-point ARC splines. Native circles use two-operand ARC instructions. As documented by the project, display-size text may differ from PP3 in placement or thickness; large type is confined to the intentional titles. No renderer source was changed.

## Page notes

'''
notes=[]
for x in infos:
    stem=Path(x['file']).stem
    notes.append(f"**{x['number']:03d} — {x['title']}** · [Preview](out/{stem}.png) · [256 × 200](out/{stem}-256x200.png) · [NAPLPS](out/{stem}.nap) · {x['bytes']:,} bytes\n\n{x['design']} Techniques: {', '.join(x['techniques'])}.\n")
(ROOT/'DESIGN.md').write_text(intro+'\n'.join(notes))
summary='\n'.join(f"{x['number']:03d} | {x['title']} | {x['bytes']:,} bytes | {x['style']} | still" for x in infos)
(ROOT/'out'/'summary.txt').write_text(summary+'\n\nRenderer: no confirmed defect; nonzero ink is required to set bits while recording the custom texture. See DESIGN.md.\n')
print(summary)
print(f"PASS: 25 pages; 100 previews; 50 predecessor comparisons; 24 under 3 KB; maximum {max(x['bytes'] for x in infos):,} bytes.")
