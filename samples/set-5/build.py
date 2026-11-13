"""Regenerate the ten pages, both requested sizes and contact sheets.

Encoding uses only the standard library. Preview assembly uses Pillow; the
NAPLPS renderer and ffmpeg produce the page images using Microstar strokes.
"""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess
import sys
from PIL import Image, ImageChops, ImageDraw

ROOT=Path(__file__).resolve().parent
RENDER=Path.home()/'devel/neoteletext-naplps/target/release/naplps-render'
FONT=Path.home()/'devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes'
sys.path.insert(0,str(ROOT/'pages'))


def render(nap,width,height,suffix='',tenths=5):
    stem=nap.with_name(nap.stem+suffix)
    ppm=stem.with_suffix('.ppm')
    png=stem.with_suffix('.png')
    cmd=[str(RENDER),'--width',str(width),'--height',str(height),'--font',str(FONT),'--tenths',str(tenths),str(nap),str(ppm)]
    result=subprocess.run(cmd,check=True,capture_output=True,text=True)
    assert not result.stderr.strip(),result.stderr
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',str(ppm),str(png)],check=True)
    return png


def contact(manifest,suffix='',thumb=(320,240)):
    tw,th=thumb
    sheet=Image.new('RGB',(5*(tw+16)+16,2*(th+38)+16),'#222930')
    draw=ImageDraw.Draw(sheet)
    for i,m in enumerate(manifest):
        path=ROOT/'out'/(Path(m['file']).stem+suffix+'.png')
        im=Image.open(path)
        im=im.resize(thumb,Image.Resampling.LANCZOS)
        x=16+(i%5)*(tw+16); y=16+(i//5)*(th+38)
        sheet.paste(im,(x,y))
        draw.text((x,y+th+7),f"{m['number']}  {m['title']}",fill='#F3ECD8')
    path=ROOT/'out'/('contact-sheet'+suffix+'.png')
    sheet.save(path)


def main():
    manifest=[]
    validation=[]
    for source in sorted((ROOT/'pages').glob('[0-9]*.py')):
        mod=runpy.run_path(str(source))
        p=mod['build']()
        nap=p.save()
        before=nap.read_bytes()
        # Regeneration tests byte reproducibility, rather than mirroring encoding.
        mod['build']().save()
        assert before==nap.read_bytes()
        m=dict(mod['META'],file=nap.name,bytes=len(before))
        manifest.append(m)
        record=dict(number=m['number'],bytes=len(before),sha256=hashlib.sha256(before).hexdigest(),seven_bit=max(before)<128,reset=before[:4].hex(' '),deterministic=True,renders=[])
        for w,h,suf in [(640,480,''),(512,400,'-512x400')]:
            path=render(nap,w,h,suf)
            im=Image.open(path)
            colours=len(im.getcolors(w*h))
            assert colours<=16 and im.size==(w,h)
            record['renders'].append(dict(size=[w,h],colours=colours,file=path.name))
        if m['animated']:
            settled=Image.open(nap.with_suffix('.png')).convert('RGB')
            record['blink_phases']=[]
            for t in (0,7,12,16):
                path=render(nap,640,480,f'-t{t:02}',t)
                delta=ImageChops.difference(settled,Image.open(path).convert('RGB')).getbbox()
                if delta:
                    assert delta[0]>=552 and delta[1]>=380 and delta[2]<=609 and delta[3]<=420,delta
                record['blink_phases'].append(dict(tenths=t,changed_bounds=delta))
        validation.append(record)
        print(f"{m['number']} | {m['title']} | {m['bytes']} bytes | covers {', '.join(map(str,m['covers']))}",flush=True)
    assert len(manifest)==10
    assert [m['number'] for m in manifest]==list(range(111,121))
    assert all(m['bytes']<6000 for m in manifest)
    assert sum(m['animated'] for m in manifest)<=3
    assert {c for m in manifest for c in m['covers']}==set(range(1,17))
    (ROOT/'out'/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (ROOT/'out'/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    contact(manifest)
    contact(manifest,'-512x400',(256,200))


if __name__=='__main__': main()
