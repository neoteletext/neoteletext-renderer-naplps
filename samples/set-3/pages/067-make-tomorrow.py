import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('067-make-tomorrow','ece1c4 191b19 c33628 c3b99d')
p.poly([(0,480),(0,294),(529,0),(640,0),(640,99)],2)
p.poly([(284,480),(640,249),(640,480)],1)
# Worker silhouette: head, raised forearm, hammer, shoulder wedge.
circle(p,195,230,38,1)
p.poly([(130,480),(127,313),(176,273),(233,284),(287,355),(260,480)],1)
p.poly([(216,300),(270,271),(317,185),(345,199),(307,312),(255,354)],1)
p.poly([(317,194),(366,110),(379,118),(335,206)],1)
p.poly([(338,116),(355,86),(418,119),(403,150)],1)
p.poly([(141,320),(109,362),(86,452),(116,462),(158,371)],1)
type(p,27,70,'MAKE',59,67,1)
type(p,28,132,'TOMORROW',42,51,1)
p.rect(0,394,335,86,0)
type(p,24,427,'WORKERS FESTIVAL',22,28,1)
type(p,24,464,'18 MAY / IRON YARD',20,26,2)
type(p,500,423,'BUILD',31,39,0,'center')
type(p,500,466,'TOGETHER',24,32,0,'center')
finish(p,67,'Make Tomorrow','Workers festival poster','Constructivist red diagonal and black silhouette',['diagonal polygons','silhouette','display typography'], 'An upward thrust of vermilion cuts behind a worker raising a hammer. Stacked headlines, a cream event ticket and a black counter-wedge create three directional forces. The festival details are fictional and sized for the low-resolution display.')
