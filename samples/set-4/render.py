#!/usr/bin/env python3
"""Generate pages and all four review sizes; assemble full and small contact sheets."""
from pathlib import Path
import subprocess,sys,concurrent.futures
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parent
RENDER=Path('/Users/andrewstuart/devel/neoteletext-naplps/target/release/naplps-render')
FONT=Path('/Users/andrewstuart/devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes')
SIZES=[(640,480),(256,200),(320,200),(512,400)]

def render(args):
    nap,wh=args;w,h=wh;suffix='' if w==640 else f'-{w}x{h}'
    ppm=nap.with_name(nap.stem+suffix+'.ppm')
    result=subprocess.run([str(RENDER),'--width',str(w),'--height',str(h),'--font',str(FONT),str(nap),str(ppm)],capture_output=True,text=True,check=True)
    if result.stderr.strip():raise RuntimeError(result.stderr)
    with Image.open(ppm) as im:im.save(ppm.with_suffix('.png'))
    ppm.unlink()

def sheet(naps,small=False):
    tw,th=(256,200) if small else (320,240)
    canvas=Image.new('RGB',(5*(tw+12)+12,5*(th+34)+12),'#252932')
    d=ImageDraw.Draw(canvas)
    for i,nap in enumerate(naps):
        path=nap.with_name(nap.stem+('-256x200' if small else '')+'.png')
        im=Image.open(path);im=im.resize((tw,th),Image.Resampling.LANCZOS)
        x=12+(i%5)*(tw+12);y=12+(i//5)*(th+34)
        canvas.paste(im,(x,y));d.text((x,y+th+8),nap.stem,fill='#ffffff')
    canvas.save(ROOT/'out'/('contact-sheet-256.png' if small else 'contact-sheet.png'))

if __name__=='__main__':
    chosen=sys.argv[1:]
    scripts=[p for p in sorted((ROOT/'pages').glob('[0-9]*.py')) if not chosen or any(p.name.startswith(n) for n in chosen)]
    for p in scripts:subprocess.run([sys.executable,str(p)],check=True)
    naps=[ROOT/'out'/(p.stem+'.nap') for p in scripts]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(render,[(p,s) for p in naps for s in SIZES]))
    allnaps=sorted((ROOT/'out').glob('*.nap'))
    sheet(allnaps);sheet(allnaps,True)
    print(f'Rendered {len(naps)} pages at four sizes.')
