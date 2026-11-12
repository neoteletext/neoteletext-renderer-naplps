from _support import *
META=dict(number=22,title='Your turn',purpose='Tic-tac-toe game in progress',style='Hand-drawn blue and red marker on ruled notebook paper',techniques=['incremental lines','native arcs','marker-width pels'],animated=False)
def build():
    p=Page('022-noughts-crosses',['f8f1df','263e7b','c44f46','cbd8d7','e4b8aa','e9e1ca'])
    for y in range(34,480,39):p.line([(0,y),(639,y)],3,1)
    p.line([(76,0),(76,479)],4,2)
    p.t(98,7,'YOUR TURN',42,57)
    p.t(100,67,'NOUGHTS & CROSSES',20,28,c=2)
    # Imperfect marker grid encoded as compact incremental strokes.
    p.pel(6)
    for y in [214,319]:p.scribble(129,y,5,.12,[1,1,3,1,1]*16,1)
    for x in [258,386]:p.scribble(x,112,.13,5,[2,2,3,2,2]*12,1)
    for x,y in [(194,160),(450,160),(322,371)]:
        p.line([(x-30,y-30),(x+3,y+2),(x+30,y+31)],2,8)
        p.line([(x+29,y-31),(x-2,y+3),(x-31,y+28)],2,8)
    for x,y in [(322,160),(194,266),(450,371)]:p.circle(x,y,36,1,False,7)
    p.t(100,431,'X TO PLAY',26,36,c=2)
    p.t(599,436,'MOVE 7',20,28,align='right')
    return p
if __name__=='__main__':run(build)
