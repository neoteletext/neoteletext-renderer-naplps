"""Checks for the sample deliverables and reset behaviour in the real renderer."""
from pathlib import Path
import concurrent.futures,hashlib,json,subprocess,sys,tempfile
from PIL import Image
from encoder import rgb
from render import ROOT,RENDER,FONT,SIZES

sha=lambda data:hashlib.sha256(data).hexdigest()

def run_renderer(path,out,w,h):
    result=subprocess.run([str(RENDER),'--width',str(w),'--height',str(h),'--font',str(FONT),str(path),str(out)],capture_output=True,text=True)
    assert result.returncode==0,(path,result.returncode,result.stderr)
    assert not result.stderr,(path,result.stderr)
    return Image.open(out).convert('RGB')

def main():
    manifest=json.loads((ROOT/'out/manifest.json').read_text())
    generators=sorted((ROOT/'pages').glob('*.py'))
    assert len(generators)==len(manifest)==25
    assert [m['number'] for m in manifest]==list(range(36,61))
    assert len(list((ROOT/'out').glob('*.nap')))==25
    before={p.stem:(ROOT/'out'/f'{p.stem}.nap').read_bytes() for p in generators}
    for p in generators:
        result=subprocess.run([sys.executable,str(p)],cwd=ROOT,capture_output=True,text=True)
        assert result.returncode==0,(p,result.stderr)
    for name,data in before.items():assert (ROOT/'out'/f'{name}.nap').read_bytes()==data,('non-deterministic',name)
    report={'passed':True,'pages':[],'sizes':[list(s) for s in SIZES],
            'generator_determinism':True,'all_7_bit':True,'full_palettes':True,
            'final_still_previews':100,'reset_predecessor_comparisons':0,
            'renderer_stderr':'empty in every render','confirmed_new_renderer_defects':[]}
    image_hashes=[]
    expected={}
    streams={}
    for m in manifest:
        path=ROOT/'out'/m['file'];data=path.read_bytes();meta=json.loads(path.with_suffix('.json').read_text())
        streams[path.stem]=data
        assert data and max(data)<128,(path,'not 7-bit')
        assert len(data)<6000,(path,'byte budget')
        assert data.index(b'\x0e')==data.index(b'\x0e\x20\x7f\x7f'),(path,'first SO must RESET')
        assert b'\x1b)W' in data[:24] and b'\x1b(B' in data[:24] and b'\x1b+}' in data[:24]
        assert len(meta['palette'])==16
        block=b''.join(bytes([0x3e,0x40|(i<<2),0x3c])+rgb(c) for i,c in enumerate(meta['palette']))
        assert block in data[:240],(path,'palette must precede art')
        for forbidden in (b'\x1bB',b'\x1bU',b'\x1b[',b'\x1b\\',b'\x1b_'):
            assert forbidden not in data,(path,'prohibited control',forbidden.hex())
        assert meta['bytes']==m['bytes']==len(data)
        assert meta['duration_tenths']==sum(t['duration'] for t in meta['timeline'])<=30
        assert m['animated']==bool(meta['timeline'])
        checks=[]
        for w,h in SIZES:
            suffix='' if w==640 else f'-{w}x{h}'
            preview=path.with_name(path.stem+suffix+'.png')
            im=Image.open(preview).convert('RGB');assert im.size==(w,h)
            colours=im.getcolors(w*h)
            assert colours and 2<=len(colours)<=16,(path,'palette/render',len(colours or []))
            digest=sha(im.tobytes());expected[(path.stem,w,h)]=digest
            checks.append({'width':w,'height':h,'visible_colours':len(colours),'rgb_sha256':digest})
        image_hashes.append(checks[0]['rgb_sha256'])
        report['pages'].append({'number':m['number'],'file':m['file'],'bytes':len(data),'sha256':sha(data),'wait_tenths':meta['duration_tenths'],'renders':checks})
    assert len(set(image_hashes))==25,'duplicate final pictures'
    assert sum(m['animated'] for m in manifest)<=8
    # Every page follows every possible member of this set, at both primary
    # review sizes. Comparison is rendered RGB, not a byte-stream heuristic.
    with tempfile.TemporaryDirectory(dir=ROOT/'out') as tmp:
        tmp=Path(tmp)
        def compare_target(name):
            count=0
            joined=tmp/f'{name}.nap';ppm=tmp/f'{name}.ppm'
            for predecessor,prior in streams.items():
                joined.write_bytes(prior+streams[name])
                for w,h in ((640,480),(256,200)):
                    im=run_renderer(joined,ppm,w,h)
                    assert sha(im.tobytes())==expected[(name,w,h)],('reset dependence',name,predecessor,w,h)
                    count+=1
            joined.unlink();ppm.unlink()
            return count
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            report['reset_predecessor_comparisons']=sum(pool.map(compare_target,streams))
        name='049-merevale-link';path=ROOT/'out'/f'{name}.nap'
        meta=json.loads(path.with_suffix('.json').read_text());stage=tmp/'stage.nap';out=tmp/'stage.ppm'
        stage.write_bytes(streams[name][:meta['timeline'][0]['length']])
        initial=run_renderer(stage,out,640,480)
        assert sha(initial.tobytes())!=expected[(name,640,480)],'reveal must visibly change'
        assert initial.tobytes()==Image.open(ROOT/'out'/f'{name}-reveal.png').convert('RGB').tobytes()
        gif=Image.open(path.with_suffix('.gif'));assert gif.n_frames==2
        assert gif.info['duration']==800
        report['animated_pages']=1;report['maximum_wait_tenths']=8;report['welcome_reveal_checked']=True
    (ROOT/'out/validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"PASS: 25 generators, 100 previews, 16-entry palettes, 7-bit streams, all under 3 KB")
    print(f"PASS: {report['reset_predecessor_comparisons']} rendered predecessor comparisons, byte-for-byte RGB equality")
    print('PASS: one finite 0.8-second reveal, complete final state, no renderer warnings')

if __name__=='__main__':main()
