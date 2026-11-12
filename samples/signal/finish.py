"""Build review animations and the contact sheet, entirely within this directory."""
from pathlib import Path
import json, shutil, subprocess
from render import ROOT, render


def animation(page):
    meta=json.loads(page.with_suffix('.json').read_text())
    if not meta['timeline']:return
    work=ROOT/'out'/('.frames-'+page.stem)
    work.mkdir(exist_ok=True)
    data=page.read_bytes()
    frames=[]
    try:
        # Constellation timing is sampled at 10 fps to preserve .3s reveals
        # and the independent 4/12-tenth blink cycle. Other pages change only
        # at WAIT boundaries; keep their exact intervals in the concat file.
        if page.stem.startswith('03'):
            for t in range(meta['duration_tenths']+16):
                stages=[s for s in meta['timeline'] if s['tenths']<=t]
                length=stages[-1]['length'] if t<meta['duration_tenths'] else len(data)
                frames.append((t,length,1))
        else:
            frames=[(s['tenths'],s['length'],s['duration']) for s in meta['timeline']]
            frames.append((meta['duration_tenths'],len(data),10))
        listing=[]
        for i,(t,length,duration) in enumerate(frames):
            source=work/'checkpoint.nap';source.write_bytes(data[:length]+b'\x0f')
            dest=work/f'{i:03d}.png';render(source,dest,t)
            listing.extend([f"file '{dest.name}'",f'duration {duration/10:.1f}'])
        listing.append(f"file '{dest.name}'")
        schedule=work/'frames.txt';schedule.write_text('\n'.join(listing)+'\n')
        subprocess.run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',str(schedule),'-filter_complex','[0:v]split[a][b];[a]palettegen=stats_mode=full[p];[b][p]paletteuse=dither=none','-fps_mode','vfr','-loop','0',str(page.with_suffix('.gif'))],check=True)
    finally:shutil.rmtree(work)


def contact_sheet():
    listing=ROOT/'out'/'.contact-input.txt'
    pages=sorted((ROOT/'out').glob('*.nap'))
    listing.write_text('\n'.join(f"file '{p.stem}.png'\nduration 0.04" for p in pages)+'\n')
    try:
        subprocess.run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-vf','scale=384:288:flags=area,tile=5x2:padding=16:margin=16:color=0x121e2b','-frames:v','1',str(ROOT/'out/contact-sheet.png')],check=True)
    finally:listing.unlink()

if __name__=='__main__':
    for page in sorted((ROOT/'out').glob('*.nap')):animation(page)
    contact_sheet()
