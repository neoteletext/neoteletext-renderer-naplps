from _support import *

META=dict(number=114,title='North Quay Radio',purpose='A settled harbour watch log showing the latest received messages',style='Teal phosphor terminal with a cream title and amber channel badge',techniques=['active FIELD','automatic character-edge wrapping','CR/LF inside FIELD','SCROLL ON and OFF','colour mode 2','3/2 row spacing'],covers=[4,8,12],animated=False)

def build():
    p=Page('114-quay-radio',['071F25','A6DAC7','F2D993','31555B','0D3037','F3EAD6','D5925C','F3EAD6'])
    p.t(32,22,'NORTH QUAY',34,43,5)
    p.t(32,70,'RADIO / WATCH LOG',19,27,1)
    p.rect(484,25,124,68,2)
    p.t(546,32,'CH 06',19,26,0,align='center')
    p.t(546,63,'18:42',15,22,0,align='center')
    rule(p,117,3)
    p.t(40,132,'TIME   STATION   /   RECEIVED MESSAGE',12,18,2,prop=False)
    p.rect(32,158,576,258,3,False)
    p.style(14.0625,20,rows=2).field(40,166,562.5,240).cmd(0x3e,b'\x44\x40').pos(40,187).raw(SCROLL)
    lines=['18:30  TERN      / DEPARTING EAST PIER',
           '18:31  QUAY      / CHANNEL CLEAR',
           '18:33  LANTERN   / INBOUND AT MARK TWO',
           '18:34  QUAY      / PILOT ADVISED',
           '18:35  TERN      / PASSING GREEN MARK',
           '18:36  QUAY      / WIND SOUTH, FORCE 2',
           '18:37  LANTERN   / REQUEST BERTH FOUR',
           '18:38  QUAY      / BERTH FOUR RESERVED',
           '18:39  TERN      / CLEAR OF THE HARBOUR',
           '18:40  QUAY      / LANTERN, COME AHEAD']
    start=len(p.data)
    p.write('\r\n'.join(lines)+'\r\n')
    # Exactly 40 cells on the first line: next text wraps within the active field.
    p.write('18:41  LANTERN   / ALL LINES FAST'.ljust(40)+'       QUAY     / WELCOME HOME\r\n18:42  QUAY      / WATCH COMPLETE')
    p.evidence_note('scroll-and-wrap',start,columns=40,field=[40,166,560,240],discarded_prefix='18:30')
    p.raw(NOSCROLL).field()
    footer(p,114,'ARCHIVE 06-18  /  LAST EIGHT LINES',1)
    return p

if __name__=='__main__': finish(build,META)
