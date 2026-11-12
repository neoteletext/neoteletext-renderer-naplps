#!/usr/bin/env python3
"""Generate streams, render four terminal sizes, and assemble review sheets."""
from pathlib import Path
import importlib.util
import sys
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out'
RENDER='/Users/andrewstuart/devel/neoteletext-naplps/target/release/naplps-render'
FONT='/Users/andrewstuart/devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes'
sys.path.insert(0,str(ROOT/'pages'))
SIZES=[(640,480,''),(256,200,'-256'),(320,200,'-320'),(512,400,'-512')]

def render(job):
    path,w,h,suffix=job
    ppm=path.with_name(path.stem+suffix+'.ppm')
    result=subprocess.run([RENDER,'--width',str(w),'--height',str(h),'--font',FONT,str(path),str(ppm)],capture_output=True,check=True)
    assert not result.stderr, result.stderr.decode()
    with Image.open(ppm) as im:im.save(ppm.with_suffix('.png'))
    ppm.unlink()

def sheets(entries):
    for suffix,w,h,name in [('',320,240,'contact-sheet'),('-256',256,200,'contact-sheet-256')]:
        sheet=Image.new('RGB',(5*w,5*(h+24)), '#252b33')
        draw=ImageDraw.Draw(sheet)
        for i,m in enumerate(entries):
            src=OUT/(Path(m['file']).stem+suffix+'.png')
            if not src.exists():continue
            with Image.open(src) as im:sheet.paste(im.resize((w,h),Image.Resampling.LANCZOS),(i%5*w,i//5*(h+24)))
            draw.text((i%5*w+7,i//5*(h+24)+h+5),f"{m['number']:03d}  {m['title']}",fill='#f5f4e9')
        sheet.save(OUT/(name+'.png'))
    for start in range(0,len(entries),5):
        row=entries[start:start+5]
        sheet=Image.new('RGB',(1280,3*504),'#252b33')
        draw=ImageDraw.Draw(sheet)
        for j,m in enumerate(row):
            with Image.open(OUT/Path(m['file']).with_suffix('.png')) as im:sheet.paste(im,(j%2*640,j//2*504))
            draw.text((j%2*640+8,j//2*504+485),f"{m['number']:03d}  {m['title']}",fill='white')
        sheet.save(OUT/f"review-{row[0]['number']:03d}-{row[-1]['number']:03d}.png")

def main():
    entries=[]; jobs=[]
    for f in sorted((ROOT/'pages').glob('[0-9]*.py')):
        if len(sys.argv)>1 and f.name[:3] not in sys.argv[1:]:continue
        spec=importlib.util.spec_from_file_location('page_'+f.stem.replace('-','_'),f)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        p=mod.build();path=p.save()
        meta=dict(mod.META,file=path.name,bytes=path.stat().st_size)
        entries.append(meta)
        jobs.extend((path,w,h,suffix) for w,h,suffix in SIZES)
    with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(render,jobs))
    for m in entries:
        if not m['animated']:continue
        path=OUT/m['file'];ppm=OUT/(path.stem+'-blink-005.ppm')
        result=subprocess.run([RENDER,'--font',FONT,'--tenths','5',str(path),str(ppm)],capture_output=True,check=True)
        assert not result.stderr,result.stderr.decode()
        with Image.open(ppm) as im:im.save(ppm.with_suffix('.png'))
        ppm.unlink()
        with Image.open(path.with_suffix('.png')) as a, Image.open(ppm.with_suffix('.png')) as b:
            a.save(path.with_suffix('.gif'),save_all=True,append_images=[b],duration=[500,1000],loop=0)
    if len(sys.argv)==1:
        (OUT/'manifest.json').write_text(json.dumps(entries,indent=2)+'\n')
        sheets(entries)
    print(f'Rendered {len(entries)} pages at all four sizes.')
if __name__=='__main__':main()
