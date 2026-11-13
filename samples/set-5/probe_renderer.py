"""Minimal, reproducible raster comparisons for the observations in DESIGN.md.

No renderer code is changed. Probe NAP streams and both image sizes are kept.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
import json
from encoder.text import Page
from build import render

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out'/'probes'
OUT.mkdir(parents=True,exist_ok=True)

CASES=[('fixed-e-mode1',b'e',0,None,100),
       ('fixed-acute-mode1',b'\x19\x42e',0,None,100),
       ('fixed-e-mode2',b'e',0,0,100),
       ('fixed-acute-mode2',b'\x19\x42e',0,0,100),
       ('prop-ill-mode1',b'ill',3,None,100),
       ('prop-ill-mode2',b'ill',3,0,100),
       ('prop-last-l-mode2',b'l',3,0,132)]


def main():
    report=[]
    for name,text,spacing,bg,x in CASES:
        p=Page('probes/'+name,['F0E7D4','193E50','BA5037','999999','888888','777777','666666','F0E7D4'])
        p.at(x,220,text,w=64,h=80,c=1,spacing=spacing,bg=bg)
        nap=p.save()
        for w,h,suffix in [(640,480,''),(512,400,'-512x400')]:
            render(nap,w,h,suffix)
    for suffix in ('','-512x400'):
        ims={name:Image.open(OUT/(name+suffix+'.png')).convert('RGB') for name,*_ in CASES}
        def diff(a,b):
            delta=ImageChops.difference(ims[a],ims[b])
            return sum(count for count,pixel in delta.getcolors(delta.width*delta.height) if pixel!=(0,0,0))
        r=dict(size=list(ims['fixed-e-mode1'].size),
               mode1_acute_changes_pixels=diff('fixed-e-mode1','fixed-acute-mode1'),
               mode2_acute_changes_pixels=diff('fixed-e-mode2','fixed-acute-mode2'),
               mode2_ill_equals_only_last_l=diff('prop-ill-mode2','prop-last-l-mode2')==0,
               proportional_mode_changes_pixels=diff('prop-ill-mode1','prop-ill-mode2'))
        assert r['mode1_acute_changes_pixels']>0
        assert r['mode2_acute_changes_pixels']==0
        assert r['mode2_ill_equals_only_last_l']
        assert r['proportional_mode_changes_pixels']>0
        report.append(r)
    (OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    # Crops are shown at native 640-render scale; text outside the crop supplies labels.
    sheet=Image.new('RGB',(790,350),'#222930')
    d=ImageDraw.Draw(sheet)
    names=['fixed-acute-mode1','fixed-acute-mode2','prop-ill-mode1','prop-ill-mode2']
    for i,name in enumerate(names):
        x=(i%2)*390+10; y=(i//2)*170+10
        d.text((x,y),name,fill='#F0E7D4')
        im=Image.open(OUT/(name+'.png')).crop((75,130,250,235))
        sheet.paste(im,(x,y+25))
    sheet.save(OUT/'comparison.png')
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()
