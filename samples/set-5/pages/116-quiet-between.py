from _support import *

META=dict(number=116,title='The Quiet Between',purpose='A four-stanza broadside poem for a reading room',style='Pale blue paper, deep blue type and a distant ochre moon',techniques=['character spacing 1, 5/4, 3/2 and proportional','row spacing 1, 5/4, 3/2 and 2','CR/LF in stanza fields'],covers=[3,4,12],animated=False)

def build():
    p=Page('116-quiet-between',['DBE6E3','264F61','BF8A47','AAC4C7','829FA9','F7F0D9','4F7886','264F61'])
    p.t(32,20,'THE QUIET',40,50,1)
    p.t(32,72,'BETWEEN',40,50,1)
    p.circle(556,64,29,2)
    stanzas=[(40,157,0,0,'I / NEAR','One bell\r\non still water.\r\nWe listen.'),
             (344,157,1,1,'II / FAR','Two lights\r\nbeyond the bay.\r\nWe linger.'),
             (40,285,2,2,'III / AIR','A sail\r\nunthreads\r\nthe blue.'),
             (344,285,3,3,'IV / HOME','The tide returns.\r\nAn open door.\r\nEnough.')]
    for x,y,spacing,rows,cap,s in stanzas:
        p.t(x,y,cap,10,14,2)
        p.style(12,20,spacing=spacing,rows=rows).field(x,y+24,256,112).pos(x,y+45).color(1).write(s).field()
    p.poly([(0,431),(80,423),(175,434),(280,421),(394,432),(502,422),(640,430),(640,480),(0,480)],3)
    p.t(32,449,'NESSA VENN  /  READING ROOM EDITION 04',10,14,1)
    p.t(608,449,'116',10,14,1,align='right')
    return p

if __name__=='__main__': finish(build,META)
