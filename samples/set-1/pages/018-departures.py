from _support import *
META=dict(number=18,title='Alderfield departures',purpose='Airport departures board',style='Yellow split-flap lettering on black with individual character cells',techniques=['colour mode 2','fixed-pitch text','rules'],animated=False)
def build():
    p=Page('018-departures',['080b0d','ffe365','292c2a','a29c61','191d1f','f9efb1'])
    p.poly([(30,26),(38,26),(39,44),(60,56),(60,63),(39,58),(38,78),(44,82),(44,87),(33,83),(22,87),(22,82),(28,78),(27,58),(7,63),(7,56),(28,44)],1)
    p.t(84,14,'DEPARTURES',35,49)
    p.t(84,65,'ALDERFIELD  /  18:40',20,28,c=3)
    for x,s in [(17,'TIME'),(130,'FLT'),(246,'TO'),(441,'GT'),(504,'STATE')]:p.t(x,111,s,18,27,c=3)
    rows=[('18:55','AV204','EASTPORT','04','BOARD'),('19:10','NX318','ELMHAVEN','12','CALL'),('19:35','AV086','LARCH','07','ON TM'),('20:00','QH512','WEST ISLE','03','ON TM')]
    for row,fields in enumerate(rows):
        y=155+row*65
        for x,s in zip([17,130,246,441,504],fields):
            p.rect(x,y,len(s)*20,39,4)
            p.t(x+1,y+2,s,20,33,c=1,prop=False,bg=4)
            # Narrow cell dividers and a lower flap edge leave glyphs intact.
            for j in range(1,len(s)):
                p.line([(x+j*20,y),(x+j*20,y+39)],0,1)
            p.line([(x,y+35),(x+len(s)*20,y+35)],2,1)
    p.line([(16,425),(623,425)],2,2)
    p.t(17,441,'GATES CLOSE 10 MIN BEFORE',20,27,c=5,prop=False)
    return p
if __name__=='__main__':run(build)
