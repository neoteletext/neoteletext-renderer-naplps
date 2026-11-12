from _support import *
META=dict(number=21,title='Les petits mots',purpose='French vocabulary flash cards with accents',style='Playful offset paper cards and small illustrative word pictures',techniques=['supplementary set','native arcs','polygons'],animated=False)
def build():
    p=Page('021-french-cards',['f5c15a','303957','fff6df','f5b8a8','b4d7b0','a9d4e8','dfbddd','ce9250','729b72'])
    p.t(24,8,'LES PETITS MOTS',34,47)
    p.t(615,26,'FR / EN',20,28,align='right')
    cards=[(20,87,3,'école','school'),(334,79,4,'forêt','forest'),(27,284,5,'café','coffee'),(341,278,6,'été','summer')]
    for x,y,col,word,eng in cards:
        p.rect(x+7,y+7,270,174,7);p.rect(x,y,270,174,2)
        p.rect(x+12,y+12,95,98,col)
        p.t(x+120,y+28,word,27,39)
        p.t(x+120,y+87,eng,20,28)
    # School building, including bell tower.
    p.poly([(45,136),(80,108),(115,136)],1);p.rect(52,136,57,43,3)
    p.rect(75,151,14,28,1);p.rect(57,144,9,10,2);p.rect(95,144,9,10,2)
    p.line([(80,109),(80,99)],1,2);p.poly([(80,99),(96,103),(80,107)],1)
    # Forest: three evergreen silhouettes.
    for x,y in [(366,159),(388,142),(411,166)]:
        p.rect(x-3,y,6,15,1);p.poly([(x,y-54),(x-19,y),(x+19,y)],8)
    # Cup and saucer; steam uses true three-point arcs.
    p.rect(56,324,49,34,1);p.circle(111,337,12,1,False,4)
    p.line([(49,366),(114,366)],1,4)
    p.arc((71,315),(66,305),(73,296),1)
    p.arc((87,315),(82,305),(89,296),1)
    sun(p,400,336,22,7)
    return p
if __name__=='__main__':run(build)
