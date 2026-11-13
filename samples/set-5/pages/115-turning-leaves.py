from _support import *

META=dict(number=115,title='Turning Leaves',purpose='A library display of books to read from a different angle',style='Ochre and oxblood book cloth against warm white',techniques=['all four text paths','all four rotations','90-degree upward spine','270-degree downward spine','180-degree leftward cover title'],covers=[5,6],animated=False)

def build():
    p=Page('115-turning-leaves',['E9E1CA','26382E','AD513D','DBAC54','7A3844','F4EBD5','879076','26382E'])
    p.t(32,22,'TURNING LEAVES',32,42,1)
    p.t(32,74,'A LIBRARY DISPLAY  /  STORIES WITH ANOTHER SIDE',12,18,1)
    p.rect(39,127,103,289,6)
    p.rect(47,119,103,289,2)
    p.rect(166,147,103,269,6)
    p.rect(174,139,103,269,4)
    p.rect(300,127,296,289,6)
    p.rect(308,119,296,289,3)
    for x,y,w,h in [(47,119,103,289),(174,139,103,269),(308,119,296,289)]:
        p.rect(x+9,y+10,w-18,h-20,5,False)
    p.at(111,380,'THE LONG WAY',w=18,h=28,c=5,path=2,rotation=1)
    p.at(208,157,'A RIVER BELOW',w=16,h=28,c=5,path=3,rotation=3)
    p.t(455,136,'A TWO-WAY NOVEL',12,18,1,align='center')
    p.t(455,178,'BEFORE',29,40,1,align='center')
    p.t(455,219,'THE RAIN',29,40,1,align='center')
    p.line([(343,277),(568,277)],1,2)
    # Reading the second title requires turning the book: rotation AND left path.
    p.at(562,307,'AFTER THE',w=24,h=34,c=4,path=1,rotation=2)
    p.at(526,350,'FLOOD',w=28,h=36,c=4,path=1,rotation=2)
    footer(p,115,'EAST ROOM  /  BORROW A DIFFERENT POINT OF VIEW',1)
    return p

if __name__=='__main__': finish(build,META)
