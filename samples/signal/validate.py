"""Artifact and state-independence checks; no third-party Python packages."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
from encoder import xy,rgb
from render import ROOT,RENDER,FONT


def render_rgb(source,dest,tenths=0):
    result=subprocess.run([str(RENDER),'--width','640','--height','480','--palette-bits','4','--tenths',str(tenths),'--font',str(FONT),str(source),str(dest)],capture_output=True,text=True,check=True)
    if result.stderr:raise AssertionError(result.stderr)
    header,raster=dest.read_bytes().split(b'\n255\n',1)
    assert header==b'P6\n640 480' and len(raster)==640*480*3
    return raster


def validate():
    # Published default-domain example, plus the four pure GRB encodings.
    assert xy(.5,.25,3)==b'Q@@'
    assert xy(-1/256,0,3)==b'xxx'
    assert rgb('ffffff')==b'\x7f'*4
    assert rgb('ff0000')==b'R'*4
    assert rgb('00ff00')==b'd'*4
    assert rgb('0000ff')==b'I'*4
    pages=sorted((ROOT/'out').glob('*.nap'))
    assert len(pages)==10
    work=ROOT/'out'/'.validation';work.mkdir(exist_ok=True)
    rows=['file\tbytes\tsha256\trendered_colours\treset_independent\twait_stages']
    try:
        for i,page in enumerate(pages):
            data=page.read_bytes();meta=json.loads(page.with_suffix('.json').read_text())
            assert 0<len(data)<8192 and max(data)<128
            assert data.startswith(b'\x1b%A\x18\x1b"F\x1bE\x0e\x20\x7f\x7f')
            assert len(meta['palette'])==16 and meta['bytes']==len(data)
            reference=render_rgb(page,work/'single.ppm')
            colours=len(set(zip(reference[0::3],reference[1::3],reference[2::3])))
            assert 1<colours<=16
            combined=work/'combined.nap'
            combined.write_bytes(pages[(i-1)%10].read_bytes()+data)
            assert render_rgb(combined,work/'combined.ppm')==reference, f'{page}: inherited state'
            # Source scripts reproduce byte-for-byte identical streams.
            subprocess.run([sys.executable,str(ROOT/'pages'/f'{page.stem}.py')],cwd=ROOT,check=True,capture_output=True)
            assert page.read_bytes()==data,f'{page}: non-deterministic generator'
            if page.stem.startswith('03'):
                assert render_rgb(page,work/'blink.ppm',4)!=reference
                assert render_rgb(page,work/'blink.ppm',16)==reference
            stages=[]
            for f in meta['frames']:
                prefix=work/'prefix.nap';prefix.write_bytes(data[:f['length']]+b'\x0f')
                stages.append(hashlib.sha256(render_rgb(prefix,work/'stage.ppm')).digest())
            if stages:assert len(set(stages))==len(stages),f'{page}: duplicate key moments'
            rows.append(f'{page.name}\t{len(data)}\t{hashlib.sha256(data).hexdigest()}\t{colours}\tyes\t{len(meta["timeline"])}')
            print(f'{page.name}: {len(data)} bytes, {colours} colours, reset-independent, deterministic')
        (ROOT/'out/manifest.tsv').write_text('\n'.join(rows)+'\n')
    finally:shutil.rmtree(work)
    print('PASS: 10 pages; 7-bit streams; <8 KiB; 640x480; <=16 rendered colours; clean renderer stderr; independent resets; distinct key moments.')

if __name__=='__main__':validate()
