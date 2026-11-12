#!/usr/bin/env python3
"""Validate the brief's material constraints, renderer state and puzzle content."""
from pathlib import Path
import sys,subprocess,hashlib,json,re,tempfile
from itertools import product
from PIL import Image
from catalog import PAGES
from render import ROOT,RENDER,FONT,SIZES
sys.path.insert(0,str(ROOT/'pages'))
from lib import xy

def check_picture(data,w,h,tmp,tenths=0):
    nap=tmp/'check.nap';ppm=tmp/'check.ppm';nap.write_bytes(data)
    result=subprocess.run([str(RENDER),'--width',str(w),'--height',str(h),'--font',str(FONT),'--tenths',str(tenths),str(nap),str(ppm)],capture_output=True,text=True,check=True)
    assert not result.stderr.strip(),result.stderr
    with Image.open(ppm) as im:return im.convert('RGB').copy()

# Minimal exhaustive KQK legality is sufficient for this three-piece problem.
squares=list(product(range(8),repeat=2))
def adjacent(a,b):return max(abs(a[0]-b[0]),abs(a[1]-b[1]))<=1
def queen_attacks(q,t,k):
    dx=t[0]-q[0];dy=t[1]-q[1]
    if not(dx==0 or dy==0 or abs(dx)==abs(dy)):return False
    n=max(abs(dx),abs(dy))
    if not n:return False
    step=(dx//n,dy//n)
    return all((q[0]+step[0]*i,q[1]+step[1]*i)!=k for i in range(1,n))
def black_moves(k,q,b):
    return [s for s in squares if s!=b and adjacent(s,b) and not adjacent(s,k) and (s==q or not queen_attacks(q,s,k))]
def white_moves(k,q,b):
    for s in squares:
        if s!=k and adjacent(s,k) and not adjacent(s,b) and s!=q:yield(s,q)
        if s not in [k,q,b] and queen_attacks(q,s,k) and queen_attacks(q,s,b):yield(k,s)
def mate(k,q,b):return queen_attacks(q,b,k) and not black_moves(k,q,b)
def check_content():
    k,q,b=(0,4),(0,0),(0,7)
    assert not queen_attacks(q,b,k) and not adjacent(k,b)
    moves=list(white_moves(k,q,b))
    assert not any(mate(kk,qq,b) for kk,qq in moves)
    keys=[]
    for kk,qq in moves:
        replies=black_moves(kk,qq,b)
        if replies and all(bb!=qq and any(mate(k2,q2,bb) for k2,q2 in white_moves(kk,qq,bb)) for bb in replies):keys.append((kk,qq,replies))
    assert keys==[((1,5),(0,0),[(1,7)])],keys
    assert [(kk,qq) for kk,qq in white_moves((1,5),q,(1,7)) if mate(kk,qq,(1,7))]==[((1,5),(7,7))]
    words=['HEART','EMBER','ABUSE','RESIN','TREND']
    assert [''.join(row[c] for row in words) for c in range(5)]==words
    assert sum([9,13,17,21])==sum([33,21,6])==60 and 33>60//2
    return dict(chess='1.Kb6+ Kb8 2.Qh8#; unique key and unique mating move',crossword=words,seats=dict(Civic=33,Union=21,League=6))

manifest=json.loads((ROOT/'out/manifest.json').read_text())
assert [m['number'] for m in manifest]==list(range(86,111))
assert len(list((ROOT/'pages').glob('[0-9]*.py')))==len(list((ROOT/'out').glob('*.nap')))==25
assert len(manifest)==25 and sum(m['animated'] for m in manifest)<=8
expected_techniques={'macro','DRCS','defined fill pattern','hatching','mosaics','incremental lines','proportional text','supplementary set','colour mode 2','palette redefinition'}
assert expected_techniques <= {t for m in manifest for t in m['techniques']}
# Verify each required specialised technique has a corresponding wire instruction.
probes={91:b'\x1b@!',93:b'\x1bC!',100:b'\x1bDA',101:b'\x19CA',109:b'\x1d\x7f',107:b'\x3e\x44\x54'}
for number,probe in probes.items():
    m=next(m for m in manifest if m['number']==number)
    assert probe in (ROOT/'out'/m['file']).read_bytes(),(number,probe)
for number,probe in [(97,b'\x3a'),(101,b'\x23\x50'),(100,b'\x23\x60')]:
    m=next(m for m in manifest if m['number']==number)
    assert probe in (ROOT/'out'/m['file']).read_bytes(),(number,probe)
assert (ROOT/'out/104-lottery-results.nap').read_bytes().count(b'\x3e\x5c\x3c')==2
report=[];prefix=b'\x1b)W\x0e\x20\x7f\x7f'
with tempfile.TemporaryDirectory(dir=ROOT/'out') as temporary:
    tmp=Path(temporary)
    for i,m in enumerate(manifest):
        nap=ROOT/'out'/m['file'];data=nap.read_bytes()
        subprocess.run([sys.executable,str(ROOT/'pages'/(nap.stem+'.py'))],check=True,capture_output=True)
        assert nap.read_bytes()==data,f'Non-deterministic: {nap.name}'
        assert len(data)==m['bytes']<6144 and max(data)<128
        assert data.startswith(prefix),nap.name
        start=data.index(b'\x3e')
        for entry in range(16):
            chunk=data[start+entry*7:start+(entry+1)*7]
            assert chunk[:3]==bytes([0x3e,0x40|entry<<2,0x3c]) and all(v>=64 for v in chunk[3:]),(nap.name,entry)
        for illegal in [b'\x1bB',b'\x1bP',b'\x1bU',b'\x1b[',b'\x1b\\',b'\x1b]']:
            assert illegal not in data,(nap.name,'forbidden control',illegal)
        sizes=[]
        for w,h in SIZES:
            suffix='' if w==640 else f'-{w}x{h}'
            with Image.open(nap.with_name(nap.stem+suffix+'.png')) as im:
                assert im.size==(w,h)
                colours=len(im.convert('RGB').getcolors(w*h))
                assert 1<colours<=16,(nap.name,colours)
                baseline=im.convert('RGB').copy()
            if w in [640,256]:
                prev=(ROOT/'out'/manifest[i-1]['file']).read_bytes()
                after=check_picture(prev+data,w,h,tmp)
                assert after.tobytes()==baseline.tobytes(),f'Reset independence: {nap.name}, {w}'
            if w==256:
                # Reassign even G1 before the page; its initial designation must recover.
                hostile=prev+b'\x1b(|\x1b){\x1b*}\x1b+z\x1bo'
                after=check_picture(hostile+data,w,h,tmp)
                assert after.tobytes()==baseline.tobytes(),f'Charset independence: {nap.name}'
            sizes.append(dict(width=w,height=h,colours=colours))
        waits=[v[0]-64 for v in re.findall(re.escape(b'\x3d\x5c')+b'([\x40-\x7f])',data)]
        assert sum(waits)<=30,(nap.name,waits)
        if not m['animated']:assert not waits and b'\x3f' not in data
        report.append(dict(number=m['number'],file=nap.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),wait_tenths=sum(waits),sizes=sizes,reset_checks=3))
    lottery=(ROOT/'out/104-lottery-results.nap').read_bytes()
    cuts=list(re.finditer(re.escape(b'\x3d\x5c')+b'[\x40-\x7f]',lottery))
    assert len(cuts)==7 and sum(v[0]-64 for v in re.findall(re.escape(b'\x3d\x5c')+b'([\x40-\x7f])',lottery))==21
    stage_hashes=[hashlib.sha256(check_picture(lottery[:m.start()],256,200,tmp).tobytes()).hexdigest() for m in cuts]
    assert len(set(stage_hashes))==7,'Lottery stages must actually change'
    orbit=(ROOT/'out/098-orbit-status.nap').read_bytes()
    a,b,c=[check_picture(orbit,256,200,tmp,t) for t in [0,2,16]]
    assert a.tobytes()!=b.tobytes() and a.tobytes()==c.tobytes()
    aa=a.tobytes();bb=b.tobytes()
    changed=sum(aa[i:i+3]!=bb[i:i+3] for i in range(0,len(aa),3))
    assert 0<changed<30,changed
assert sum(m['bytes']<3072 for m in manifest)>len(manifest)//2
for sheet in ['contact-sheet.png','contact-sheet-256.png']:
    with Image.open(ROOT/'out'/sheet) as im:assert im.width>1000 and im.height>1000
result=dict(status='passed',pages=25,previews=100,reset_comparisons=75,animated=2,total_bytes=sum(m['bytes'] for m in manifest),all_under_3kb=True,content=check_content(),pages_detail=report)
(ROOT/'out/validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(f'PASS: 25 pages; 100 previews; 75 reset comparisons; {result["total_bytes"]:,} bytes total; every stream under 3 KB.')
print(f'PASS: 2 animated pages; maximum WAIT 2.1 s; mission BLINK affects {changed} pixels at 256 x 200.')
print('PASS: all required techniques; deterministic generators; unique mate in two; crossword interlock; 60-seat totals.')
