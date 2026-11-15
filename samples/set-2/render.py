"""Generate selected pages and render all four review sizes (Pillow for PNG IO)."""
from pathlib import Path
import concurrent.futures,subprocess,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
RENDER=Path.home()/'devel/neoteletext-renderer-naplps/target/release/naplps-render'
FONT=Path.home()/'devel/teletext-reference/NAPLPS/fonts-extracted/data/microstar.strokes'
SIZES=[(640,480),(256,200),(320,200),(512,400)]

def render_one(path):
    for w,h in SIZES:
        suffix='' if w==640 else f'-{w}x{h}'
        ppm=ROOT/'out'/f'{path.stem}{suffix}.ppm'
        result=subprocess.run([str(RENDER),'--width',str(w),'--height',str(h),'--font',str(FONT),str(path),str(ppm)],capture_output=True,text=True,check=True)
        assert not result.stderr,(path,result.stderr)
        im=Image.open(ppm);im.save(ppm.with_suffix('.png'));ppm.unlink()
    im=Image.new('RGB',(912,508),'#bdbdbd')
    im.paste(Image.open(path.with_suffix('.png')),(0,28))
    im.paste(Image.open(ROOT/'out'/f'{path.stem}-256x200.png'),(652,28))
    d=ImageDraw.Draw(im);d.text((8,8),path.stem+' / 640 x 480',fill='black');d.text((654,8),'256 x 200 / native size',fill='black')
    review=ROOT/'out/review';review.mkdir(exist_ok=True);im.save(review/f'{path.stem}.png')
    return path.stem

def contact_sheet():
    paths=sorted((ROOT/'out').glob('*.nap'))
    im=Image.new('RGB',(1680,1360),'#172029');d=ImageDraw.Draw(im)
    for i,p in enumerate(paths):
        x=16+(i%5)*334;y=14+(i//5)*270
        tile=Image.open(p.with_suffix('.png')).resize((320,240),Image.Resampling.NEAREST)
        im.paste(tile,(x,y));d.text((x,y+247),p.stem,fill='#f5eedc')
    im.save(ROOT/'out/contact-sheet.png')
    small=Image.new('RGB',(1360,1150),'#172029');d=ImageDraw.Draw(small)
    for i,p in enumerate(paths):
        x=8+(i%5)*272;y=8+(i//5)*230
        small.paste(Image.open(ROOT/'out'/f'{p.stem}-256x200.png'),(x,y));d.text((x,y+206),p.stem,fill='#f5eedc')
    small.save(ROOT/'out/contact-sheet-small.png')

if __name__=='__main__':
    chosen=[p for p in sorted((ROOT/'pages').glob('*.py')) if not sys.argv[1:] or any(p.name.startswith(s) for s in sys.argv[1:])]
    for path in chosen:subprocess.run([sys.executable,str(path)],cwd=ROOT,check=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for name in pool.map(render_one,[ROOT/'out'/f'{p.stem}.nap' for p in chosen]):print('Rendered',name)
    contact_sheet()
