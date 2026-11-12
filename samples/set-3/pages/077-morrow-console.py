import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atelier import *
p=page('077-morrow-console','071a12 8ceca0 377e50 123322 4ebd70')
# The mask recorder treats entry zero as erase: choose a nonzero ink.
p.color(1)
# Define a scan-line texture in native pattern slot A.
p.cmd(0x23,b'\x40'+xy(12/640,12/Y_SCALE))
p.data.extend(b'\x1bDA\x0e')
p.cmd(0x33,xy(0,.12)+xy(.99,.20));p.data.extend(b'\x1bE\x0e')
p.texture(4);p.rect(0,0,640,480,3);p.texture()
type(p,26,53,'MORROW / SYS 4',30,36,1,prop=False)
p.line([(25,72),(615,72)],2,2)
for y,s in [(116,'NODE 07     ONLINE'),(160,'UPTIME      146:08:22'),(204,'LINK        1200 BAUD'),(248,'MEMORY      82% FREE')]:type(p,28,y,s,23,29,1,prop=False)
# Colour mode 2 paints the status text fields onto an explicit green background.
p.cmd(0x3e,bytes([0x40|(0<<2),0x40|(1<<2)]))
p.text(28,309,' ALL SYSTEMS NOMINAL ',23,31,None,False)
type(p,28,365,'RX',23,29,1,prop=False)
for i in range(20):p.rect(99+i*25,342,15,22,4 if i<16 else 2)
type(p,28,418,'LAST CHECK   23:48:06',23,29,1,prop=False)
type(p,28,460,'LOG 1842 / NO FAULTS',21,27,2,prop=False)
finish(p,77,'Morrow System Console','Computer network status display','Green phosphor terminal with scan lines',['defined fill pattern','colour mode 2','fixed-pitch text'], 'A fictional node reports uptime, link speed and free memory in large fixed-pitch fields. A native defined texture lays faint phosphor scan lines over the black-green ground. Explicit colour-mode-2 fields reverse the all-systems-nominal message, and a segmented receive meter provides a single compact graphic.')
