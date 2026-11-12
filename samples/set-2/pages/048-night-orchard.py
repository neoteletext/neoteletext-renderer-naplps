import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from encoder.art import Art,palette
p=Art('048-night-orchard',palette('0c0e19','76f1bd','e569c9','57bde3','9292c6','f0e88e'))
# Native six-block mosaic border; no vector imitation.
for y in (0,478):p.mosaic(0,y,[0x35,0x6a]*16,20,26,3)
for y in range(51,453,26):
    p.mosaic(0,y,[0x75],20,26,2);p.mosaic(620,y,[0x6a],20,26,2)
p.txt(49,84,'NIGHT',52,59,2)
p.txt(49,147,'ORCHARD',52,59,3)
p.txt(51,187,'BULLETIN BOARD / 1200 BAUD',21,26,4)
for y,num,s in [(241,'1','MESSAGES'),(285,'2','FILE LIBRARY'),(329,'3','CHAT ROOM'),(373,'4','SYSTEM NEWS')]:
    p.txt(58,y,num,26,31,5);p.txt(111,y,s,26,31,1)
p.txt(52,436,'ENTER CHOICE: 1-4',25,29,2)
p.save()
