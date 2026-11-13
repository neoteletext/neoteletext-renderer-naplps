from _support import *

META=dict(number=117,title='Pen & Point',purpose='A workshop card explaining four plotter coupling modes',style='Prussian-blue technical diagrams with ivory strokes and amber reference marks',techniques=['TEXT together motion','cursor leads','drawing point leads','independent motion','visible text-to-line geometry'],covers=[7,10],animated=False)

def build():
    p=Page('117-pen-and-point',['163D52','E8EFDF','F0BA61','557989','224B61','DF8C67','9FC2C2','E8EFDF'])
    p.t(32,22,'PEN & POINT',37,48,1)
    p.t(32,84,'TYPE INK  /  MOVE PEN TO B  /  TYPE X  /  DRAW',12,18,2)
    for mode,(x,y,title) in enumerate([(32,129,'01 / TOGETHER'),(336,129,'02 / CURSOR LEADS'),(32,280,'03 / POINT LEADS'),(336,280,'04 / INDEPENDENT')]):
        p.rect(x,y,272,133,3,False)
        p.t(x+12,y+10,title,12,18,1)
        p.line([(x+22,y+91),(x+241,y+91)],3)
        for bx,name in [(x+22,'A'),(x+155,'B')]:
            p.line([(bx,y+56),(bx,y+91)],2)
            p.t(bx,y+96,name,10,14,2)
        start=len(p.data)
        p.style(20,26).color(1).pos(x+22,y+86)
        p.style(20,26,motion=mode).write('INK')
        p.pos(x+155,y+86).write('X')
        p.cmd(0x28,xy((x+237)/640,(480-y-111)/Y_SCALE))
        # END flushes the line before a subsequent TEXT changes its coupling.
        p.raw(ESC+b'E').style()
        p.evidence_note('motion',start,mode=mode,origin=[x+22,y+86],pen_B=[x+155,y+86])
    p.t(32,432,'Amber marks: pen positions. Ivory: text and the next pen stroke.',10,15,1)
    p.t(608,455,'117',10,14,2,align='right')
    return p

if __name__=='__main__': finish(build,META)
