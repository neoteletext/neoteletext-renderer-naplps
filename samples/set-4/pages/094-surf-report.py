from lib import *
p=Page('094-surf-report',['15B3AD','062D4B','FFF3BE','F5A847','72DDD0','FFFFFF'])
p.text(22,59,'BREAKWATER',32,42,1)
p.text(23,103,'SURF / WED 09 JUN',21,26,1)
p.circle(139,216,81,3)
# Three broad wave silhouettes, using circles and polygonal crests.
p.poly([(0,310),(64,266),(151,263),(222,287),(284,304),(336,282),(393,301),(434,344),(640,344),(640,480),(0,480)],1)
p.arc((50,344),(184,242),(287,346),4,True)
p.arc((118,348),(202,283),(265,348),0,True)
p.poly([(54,346),(111,281),(179,265),(225,274),(254,296),(221,289),(182,299),(161,322),(165,343),(133,325),(109,329),(94,352)],5)
p.poly([(0,402),(81,380),(178,409),(280,378),(356,405),(425,390),(432,410),(352,428),(279,402),(180,432),(80,402),(0,425)],4)
# Compass with directional arrow; swell remains the primary number.
p.circle(526,180,57,1,False)
for a in [0,90,180,270]:
    q=math.radians(a);p.line([(526+43*math.cos(q),180+43*math.sin(q)),(526+56*math.cos(q),180+56*math.sin(q))],1,2)
p.center(113,'N',20,24,1,x=526)
arrow(p,(553,204),(503,158),2,4,15)
p.center(266,'NW 12 kt',22,27,1,x=526)
p.text(356,337,'1.8 m',44,49,2)
p.text(369,378,'SWELL / SW',21,25,2)
p.text(449,459,'12 SEC',25,31,2)
p.save()
