"""Regenerate / render the collection using the supplied renderer and ffmpeg.

The CLI consumes WAITs without stopping. Timed WAIT frames are therefore
rendered from exact stream prefixes at the saved command boundaries. BLINK
phases additionally use the renderer's --tenths option. No renderer edits.
"""
from pathlib import Path
import json, subprocess, sys
ROOT=Path(__file__).resolve().parent
RENDER=Path.home()/'devel/neoteletext-renderer-naplps/target/release/naplps-render'
FONT=Path.home()/'devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes'

def render(src,dest,t=0,width=640,height=480):
    ppm=dest.with_suffix('.ppm')
    subprocess.run([str(RENDER),'--width',str(width),'--height',str(height),'--palette-bits','4','--font',str(FONT),'--tenths',str(t),str(src),str(ppm)],check=True)
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',str(ppm),str(dest)],check=True)
    ppm.unlink()

def main():
    names=sys.argv[1:]
    for script in sorted((ROOT/'pages').glob('*.py')):
        if names and not any(script.stem.startswith(n) for n in names):continue
        subprocess.run([sys.executable,str(script)],cwd=ROOT,check=True)
        page=ROOT/'out'/f'{script.stem}.nap'
        render(page,page.with_suffix('.png'))
        meta=json.loads(page.with_suffix('.json').read_text())
        for f in meta['frames']:
            prefix=page.with_name(page.stem+'-checkpoint.nap')
            prefix.write_bytes(page.read_bytes()[:f['length']]+b'\x0f')
            render(prefix,page.with_name(f"{page.stem}-{f['tenths']:03d}-{f['label']}.png"),f['tenths'])
            prefix.unlink()
        if script.stem.startswith('03'):
            for t in (0,4,12):render(page,page.with_name(f'{page.stem}-blink-{t:03d}.png'),t)

if __name__=='__main__':main()
