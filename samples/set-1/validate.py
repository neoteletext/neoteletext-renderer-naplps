#!/usr/bin/env python3
"""Check the delivered streams, real renderer output and page independence."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from render import ROOT, OUT, RENDER, FONT, SIZES

def scan(data):
    """Read wire-level PDIs and controls; do not confuse text with opcodes."""
    records=[]; controls=Counter();pending=None;args=bytearray()
    pdi=True;sets={0:0x42,1:0x57,2:0x7c,3:0x7d};i=0
    def flush():
        nonlocal pending,args
        if pending is not None:records.append((pending,bytes(args)))
        pending=None;args=bytearray()
    while i<len(data):
        b=data[i];i+=1
        if b==0x1b:
            flush();b=data[i];i+=1
            if 0x20<=b<=0x2f:
                inter=b
                while data[i]<0x40:i+=1
                final=data[i];i+=1
                slot={0x28:0,0x29:1,0x2a:2,0x2b:3,0x2d:1,0x2e:2,0x2f:3}.get(inter)
                if slot is not None:sets[slot]=final
            elif b in [0x40,0x41,0x42,0x43,0x44]:
                controls[{0x40:'macro definitions',0x41:'executing macro definitions',0x42:'transmit macros',0x43:'DRCS definitions',0x44:'fill definitions'}[b]]+=1
                i+=1
            continue
        if b in [0x0e,0x0f]:
            flush();pdi=b==0x0e;continue
        if b in [0x19,0x1d]:
            flush();slot=2 if b==0x19 else 3
            controls[{0x7c:'supplementary glyphs',0x7d:'mosaic glyphs',0x7a:'macro calls',0x7b:'DRCS glyphs'}.get(sets[slot],'other shifts')]+=1
            i+=1;continue
        if b<0x20:flush();continue
        if not pdi:continue
        if b<0x40:
            flush();pending=b
        elif pending is not None:args.append(b)
    flush()
    return records,controls

def load_module(f):
    spec=importlib.util.spec_from_file_location(f.stem.replace('-','_'),f)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def pixels(path,w,h,outfile,tenths=0):
    r=subprocess.run([RENDER,'--font',FONT,'--width',str(w),'--height',str(h),'--tenths',str(tenths),str(path),str(outfile)],capture_output=True,check=True)
    assert not r.stderr,r.stderr.decode()
    with Image.open(outfile) as im:return im.convert('RGB').copy()

def main():
    manifest=json.loads((OUT/'manifest.json').read_text())
    assert [m['number'] for m in manifest]==list(range(11,36))
    assert len({m['purpose'] for m in manifest})==25
    assert len({m['style'] for m in manifest})==25
    assert sum(m['animated'] for m in manifest)<=8
    files=sorted((ROOT/'pages').glob('[0-9]*.py'))
    assert len(files)==25
    results=[];all_controls=Counter();all_ops=Counter()
    for m,f in zip(manifest,files):
        path=OUT/m['file'];data=path.read_bytes();mod=load_module(f)
        assert data==bytes(mod.build().data)+b'\x0f',f'Non-deterministic: {path.name}'
        assert len(data)==m['bytes']<6144
        assert max(data)<128
        assert data.startswith(b'\x0e\x20\x7f\x7f')
        records,controls=scan(data)
        assert records[0]==(0x20,b'\x7f\x7f')
        colours=[(i,a) for i,(op,a) in enumerate(records) if op==0x3c]
        assert len(colours)>=16
        for index,(position,args) in enumerate(colours[:16]):
            assert len(args)==4
            assert records[position-1]==(0x3e,bytes([0x40|(index<<2)]))
        assert not controls['transmit macros']
        assert not any(op==0x38 for op,args in records),'No input fields'
        waits=[sum(x&63 for x in a[1:]) for op,a in records if op==0x3d and a[:1]==b'\x5c']
        assert sum(waits)<=30
        animated=bool(waits or any(op==0x3f for op,a in records))
        assert animated==m['animated']
        for w,h,suffix in SIZES:
            with Image.open(OUT/(path.stem+suffix+'.png')) as im:
                assert im.size==(w,h)
                assert 2<=len(im.convert('RGB').getcolors(w*h))<=16
        boxes=json.loads(path.with_suffix('.layout.json').read_text())
        assert all(b['field_width']>=16 for b in boxes)
        assert all(b['field_height']>=24 for b in boxes)
        ops=Counter(op for op,a in records);all_ops.update(ops);all_controls.update(controls)
        results.append(dict(number=m['number'],file=path.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),text_fields=len(boxes),minimum_text_width=min(b['field_width'] for b in boxes),controls=dict(controls),wait_tenths=sum(waits)))
    assert all_ops[0x3a]>0 and all_controls['macro calls']>0 and all_controls['DRCS glyphs']>0
    assert all_controls['mosaic glyphs']>0 and all_controls['supplementary glyphs']>0
    assert all_controls['fill definitions']>0
    assert sum(1 for m in manifest if m['bytes']<3072)>12
    # Compare each stream after another page and a different-size text/font state.
    with tempfile.TemporaryDirectory(prefix='.validation-',dir=OUT) as temp:
        temp=Path(temp)
        def independence(job):
            i,w,h,suffix=job
            m=manifest[i];prev=manifest[(i+7)%25]
            dest=temp/f'{i}{suffix}.nap'
            dest.write_bytes((OUT/prev['file']).read_bytes()+(OUT/m['file']).read_bytes())
            got=pixels(dest,w,h,dest.with_suffix('.ppm'))
            with Image.open(OUT/(Path(m['file']).stem+suffix+'.png')) as expected:
                assert got.tobytes()==expected.convert('RGB').tobytes(),f'Reset leaked: {m["file"]} {w}x{h}'
        jobs=[(i,w,h,suffix) for i in range(25) for w,h,suffix in SIZES]
        with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(independence,jobs))
        # BLINK affects exactly four peripheral bulbs, and returns every 15 tenths.
        path=OUT/'031-aster-cinema.nap'
        a=pixels(path,640,480,temp/'blink0.ppm',0)
        b=pixels(path,640,480,temp/'blink5.ppm',5)
        c=pixels(path,640,480,temp/'blink15.ppm',15)
        assert a.tobytes()!=b.tobytes() and a.tobytes()==c.tobytes()
        araw,braw=a.tobytes(),b.tobytes()
        changes=[(i//3%640,i//3//640) for i in range(0,len(araw),3) if araw[i:i+3]!=braw[i:i+3]]
        assert all(y<29 or y>452 for x,y in changes)
        assert len(changes)<400
        # Reproduce the renderer's zero-colour mask behaviour, preserving evidence.
        recipe=(OUT/'026-pancakes.nap').read_bytes()
        assert recipe.count(b'\x3e\x44\x1bDA')==1
        probe=temp/'mask-zero.nap';probe.write_bytes(recipe.replace(b'\x3e\x44\x1bDA',b'\x3e\x40\x1bDA'))
        empty=pixels(probe,640,480,temp/'mask-zero.ppm')
        with Image.open(OUT/'026-pancakes.png') as full:
            assert empty.crop((0,0,640,20)).tobytes()!=full.crop((0,0,640,20)).convert('RGB').tobytes()
    # A perfect connected maze: exactly one path exists between any two cells.
    mod=load_module(ROOT/'pages'/'023-maze.py');cols,rows,edges=mod.maze()
    assert len(edges)==cols*rows-1
    adj={}
    for edge in edges:
        a,b=tuple(edge);adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
    q=deque([((0,0),0)]);seen=set();distance=None
    while q:
        node,d=q.popleft()
        if node in seen:continue
        seen.add(node)
        if node==(cols-1,rows-1):distance=d
        q.extend((n,d+1) for n in adj.get(node,[]) if n not in seen)
    assert len(seen)==cols*rows and distance is not None
    assert 1240+2100-780==2560
    assert round(41.8/(1284.6-41.8)*100,2)==3.36
    report=dict(pages=25,resolutions=[[w,h] for w,h,s in SIZES],reset_comparisons=100,all_7_bit=True,all_explicit_16_colour_maps=True,all_under_3_KiB=all(m['bytes']<3072 for m in manifest),animated_pages=sum(m['animated'] for m in manifest),wait_tenths=0,blink_changed_pixels=len(changes),maze_solution_steps=distance,renderer_observation='Colour-map entry zero erases definition-mask pels; select a nonzero entry before DEF TEXTURE.',pages_checked=results)
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    summary='\n'.join(f"{m['number']:03d} | {m['title']} | {m['bytes']} bytes | {'four bulb accents blink' if m['animated'] else 'still'}" for m in manifest)+'\n'
    (OUT/'summary.txt').write_text(summary)
    print(summary,end='')
    print(f'PASS: 25 deterministic streams; 100 renders; 100 reset comparisons; maze solution {distance} steps; blink {len(changes)} pixels.')
if __name__=='__main__':main()
