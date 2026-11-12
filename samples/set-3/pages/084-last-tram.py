import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('084-last-tram','151719 e6e1d3 777c79 c83d31')
# Slanting light projected through venetian blinds.
for y in range(-75,350,51):
    p.poly([(207,y),(640,y+132),(640,y+153),(207,y+21)],1)
# A single dark detective silhouette eats the blind strips.
p.poly([(253,358),(280,250),(331,230),(372,246),(419,355),(459,480),(220,480)],0)
p.poly([(276,182),(294,154),(354,153),(375,182),(409,192),(402,203),(254,203),(252,193)],0)
p.poly([(289,201),(366,201),(359,246),(341,268),(307,246)],0)
p.poly([(298,264),(329,286),(308,353),(281,305)],2)
p.poly([(356,264),(333,285),(352,350),(381,302)],2)
p.poly([(328,289),(339,289),(346,349),(332,374),(321,349)],0)
p.rect(0,0,239,242,0)
p.rect(31,29,117,6,3)
type(p,30,92,'LAST',57,66,1)
type(p,30,162,'TRAM',57,66,1)
type(p,31,206,'AT MIDNIGHT',23,30,3)
# Title and shadow separate the monochrome illustration from credit block.
p.rect(0,400,640,80,0)
type(p,28,432,'A FILM BY NELL VOSS',24,30,1)
type(p,28,467,'REX ARDEN / LILA WREN',20,26,2)
type(p,611,466,'FRIDAY',23,29,3,'right')
finish(p,84,'Last Tram at Midnight','Fictional film noir cinema poster','Venetian-blind shadows with a single red accent',['high-contrast polygons','silhouette','red accent'], 'Cream shafts of blind-filtered light cut across a faceless detective in a wide-brimmed hat. Grey lapels describe the coat without illuminating the face. A red title accent and Friday release label punctuate the otherwise monochrome cinema poster; all credits are invented.')
