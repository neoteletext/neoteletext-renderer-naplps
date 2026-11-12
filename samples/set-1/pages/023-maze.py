from _support import *
import random
META=dict(number=23,title='The long way out',purpose='Solvable maze puzzle with start and finish',style='Bold coral labyrinth on pale yellow; two inks only',techniques=['thick lines','polygons','deterministic maze'],animated=False)
def maze():
    rng=random.Random(2317);cols,rows=14,8
    seen={(0,0)};stack=[(0,0)];passages=set()
    while stack:
        x,y=stack[-1]
        opts=[(x+dx,y+dy) for dx,dy in [(1,0),(0,1),(-1,0),(0,-1)] if 0<=x+dx<cols and 0<=y+dy<rows and (x+dx,y+dy) not in seen]
        if not opts:stack.pop();continue
        n=rng.choice(opts);passages.add(frozenset([(x,y),n]));seen.add(n);stack.append(n)
    return cols,rows,passages
def build():
    p=Page('023-maze',['fff0bb','b93f3f'])
    p.t(16,3,'THE LONG WAY OUT',35,48)
    p.t(16,61,'START >',21,29)
    p.t(624,61,'> FINISH',21,29,align='right')
    cols,rows,passages=maze();ox,oy,step=26,118,42
    walls=[]
    for y in range(rows):
        for x in range(cols):
            if x<cols-1 and frozenset([(x,y),(x+1,y)]) not in passages:walls.append([(ox+(x+1)*step,oy+y*step),(ox+(x+1)*step,oy+(y+1)*step)])
            if y<rows-1 and frozenset([(x,y),(x,y+1)]) not in passages:walls.append([(ox+x*step,oy+(y+1)*step),(ox+(x+1)*step,oy+(y+1)*step)])
    for a in walls:p.line(a,1,6)
    p.line([(ox,oy+step),(ox,oy+rows*step),(ox+cols*step,oy+rows*step)],1,6)
    p.line([(ox,oy),(ox+cols*step,oy),(ox+cols*step,oy+(rows-1)*step)],1,6)
    p.arrow([(1,oy+21),(38,oy+21)],1,5,12)
    p.arrow([(ox+cols*step-12,oy+(rows-.5)*step),(638,oy+(rows-.5)*step)],1,5,12)
    return p
if __name__=='__main__':run(build)
