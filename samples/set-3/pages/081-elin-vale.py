import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('081-elin-vale','c7c2ac f1e5c7 355c5a 80958a')
p.rect(34,24,572,433,1)
# Circular cutouts on all four sides create true perforated silhouettes.
for x in range(43,602,23):
    circle(p,x,24,6,0);circle(p,x,457,6,0)
for y in range(43,450,23):
    circle(p,34,y,6,0);circle(p,606,y,6,0)
p.rect(55,46,530,389,2,False)
p.rect(64,55,512,307,2)
# Fictional naturalist's engraved profile, facing right.
p.poly([(135,344),(162,298),(221,282),(228,253),(209,228),(202,189),(211,133),(248,101),(297,107),(328,134),(332,166),(350,193),(332,201),(334,225),(316,246),(281,255),(276,283),(329,302),(353,344)],1)
p.poly([(205,182),(207,137),(231,103),(272,93),(308,107),(330,131),(329,159),(301,148),(287,127),(268,150),(239,151),(227,190)],3)
p.line([(308,175),(321,175)],2,3)
p.line([(318,210),(332,211)],2,2)
p.line([(293,225),(316,229)],2,2)
p.line([(280,255),(250,242)],2,2)
p.poly([(162,302),(216,286),(252,317),(276,285),(331,307),(355,349),(136,349)],3)
for i in range(9):p.line([(155+i*19,344),(183+i*15,310)],2,2)
for i in range(7):p.line([(213+i*11,134),(225+i*12,114)],2,2)
type(p,550,149,'80',74,88,1,'right')
type(p,550,187,'A',27,35,1,'right')
type(p,550,281,'FIELD',24,31,1,'right')
type(p,550,317,'NOTES',24,31,1,'right')
type(p,320,395,'ELIN VALE / 1828-1906',24,30,2,'center')
type(p,320,426,'AURELIA POST',23,29,2,'center')
finish(p,81,'Elin Vale','Commemorative postage stamp for a fictional naturalist','Perforated engraved duotone stamp',['perforated native circles','portrait polygons','engraved lines'], 'A sage profile portrait of the invented field naturalist Elin Vale is engraved with coarse coat and hair cuts. Circular edge perforations, an oversized 80 denomination and a double keyline make the composition unmistakably postal. The name, dates and Aurelia Post service are fictional.')
