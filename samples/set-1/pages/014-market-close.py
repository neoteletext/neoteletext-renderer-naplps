from _support import *
META=dict(number=14,title='Meridian market close',purpose='Stock market closing summary and index chart',style='Amber financial terminal with a native incremental line chart',techniques=['incremental lines','line textures','fixed-pitch text'],animated=False)
def build():
    p=Page('014-market-close',['100d06','ffbf48','b78031','46351b','ffe3a0'])
    p.t(16,10,'MERIDIAN / CLOSE',25,35,prop=False)
    p.t(16,55,'1,284.6',43,58,c=4,prop=False)
    p.t(620,66,'+41.8',31,41,align='right')
    p.t(620,107,'+3.36%',20,28,align='right')
    for y in [166,226,286,346]:
        p.texture(line=1);p.line([(83,y),(616,y)],3,2)
    p.texture()
    for y,s in [(152,'1300'),(212,'1250'),(272,'1200')]:p.t(8,y,s,17,25,c=2,prop=False)
    p.line([(83,147),(83,356),(617,356)],2,2)
    codes=[]
    # Single continuous native 2-bit trace, 100 market samples.
    for rise,runlen in [(True,12),(False,6),(True,18),(False,8),(True,15),(False,7),(True,20),(False,4),(True,10)]:
        if not rise:codes += [0,2]
        codes += [3]*runlen
        if not rise:codes += [0,2]
    # Net rise is 50 steps. Quantised dy=9/2048 unit: final y=184.5,
    # which corresponds to 1284.6 on the labelled 1200-1300 scale.
    p.pel(3).scribble(90,319.5,4.9,-2.7,codes,1)
    p.t(83,363,'09:00',18,26,c=2,prop=False)
    p.t(616,363,'16:00',18,26,c=2,prop=False,align='right')
    p.line([(16,408),(622,408)],2,2)
    p.t(16,419,'RLM  82.4 +2.1',20,27,prop=False)
    p.t(346,419,'VEX  36.8 -0.4',20,27,prop=False)
    p.t(16,451,'VOL 2.8M     ADV 42 / DEC 18',18,25,c=2,prop=False)
    return p
if __name__=='__main__':run(build)
