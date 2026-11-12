from _support import *
META=dict(number=24,title='Bright Spark',purpose='Trivia question with four answers',style='Game-show spotlights, magenta stage and diamond answer panels',techniques=['polygons','native arcs','display type'],animated=False)
def build():
    p=Page('024-quiz-show',['181533','fff4c4','f3bd43','994d9c','365c86','302b58','df6a99','7bb5be'])
    p.poly([(28,0),(115,0),(272,234)],5);p.poly([(525,0),(612,0),(368,234)],5)
    for x in [44,143,242,398,497,596]:
        p.circle(x,15,12,2);p.circle(x,15,6,1)
    p.t(320,43,'BRIGHT SPARK',42,57,c=2,align='center')
    p.t(320,112,'QUESTION 04  /  100 POINTS',20,28,c=7,align='center')
    p.t(320,172,'Which planet has',28,38,align='center')
    p.t(320,213,'the most visible rings?',28,38,align='center')
    for x,y,letter,ans,col in [(29,292,'A','MARS',4),(337,292,'B','SATURN',3),(29,381,'C','VENUS',3),(337,381,'D','MERCURY',4)]:
        p.poly([(x+21,y),(x+248,y),(x+271,y+36),(x+248,y+73),(x+21,y+73),(x,y+36)],col)
        p.circle(x+36,y+36,23,0)
        p.t(x+36,y+15,letter,27,38,c=2,align='center')
        p.t(x+80,y+15,ans,24,38)
    return p
if __name__=='__main__':run(build)
