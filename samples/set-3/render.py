"""Generate all pages, render actual NAPLPS at four terminal resolutions."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess, sys
from PIL import Image, ImageOps, ImageDraw
ROOT=Path(__file__).resolve().parent
RENDER='/Users/andrewstuart/devel/neoteletext-naplps/target/release/naplps-render'
FONT='/Users/andrewstuart/devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes'
def render(job):
    src,w,h=job
    suffix='' if w==640 else f'-{w}x{h}'
    dst=src.with_name(src.stem+suffix+'.ppm')
    r=subprocess.run([RENDER,'--width',str(w),'--height',str(h),'--font',FONT,str(src),str(dst)],capture_output=True,text=True)
    if r.returncode or r.stderr:raise RuntimeError((src,r.returncode,r.stderr))
    with Image.open(dst) as im:im.save(dst.with_suffix('.png'))
    dst.unlink()
if __name__=='__main__':
    if '--generate' in sys.argv:
        for p in sorted((ROOT/'pages').glob('*.py')):subprocess.run([sys.executable,str(p)],check=True)
    files=sorted((ROOT/'out').glob('*.nap'))
    with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(render,[(f,w,h) for f in files for w,h in [(640,480),(256,200),(320,200),(512,400)]]))
    for small in [False,True]:
        tw,th=(256,200) if small else (320,240)
        sheet=Image.new('RGB',(5*(tw+12)+12,5*(th+32)+12),'#18212b');d=ImageDraw.Draw(sheet)
        for i,f in enumerate(files):
            im=Image.open(f.with_name(f.stem+('-256x200' if small else '')+'.png'))
            if not small: im=im.resize((tw,th),Image.Resampling.LANCZOS)
            x=12+(i%5)*(tw+12);y=12+(i//5)*(th+32)
            sheet.paste(im,(x,y));d.text((x,y+th+5),f.stem,fill='white')
        sheet.save(ROOT/'out'/('contact-sheet-small.png' if small else 'contact-sheet.png'))
    print('Rendered',len(files),'pages at four resolutions.')
