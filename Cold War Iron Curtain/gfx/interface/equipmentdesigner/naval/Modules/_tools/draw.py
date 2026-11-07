import sys
from PIL import Image
BRIGHT={'G':(140,255,197),'R':(254,136,136),'B':(140,182,255),'Y':(197,162,33),'W':(255,255,255)}
DARK={'G':(80,161,129),'R':(161,79,79),'B':(87,114,161),'Y':(124,103,19),'W':(177,177,177)}
FONT={
'S':[".###.","#...#","#....","#....",".###.","....#","....#","#...#",".###."],
'A':[".###.","#...#","#...#","#...#","#####","#...#","#...#","#...#","#...#"],
'M':["#...#","#...#","##.##","#.#.#","#.#.#","#...#","#...#","#...#","#...#"],
'N':["#...#","#...#","##..#","#.#.#","#.#.#","#..##","#...#","#...#","#...#"],
'8':[".###.","#...#","#...#","#...#",".###.","#...#","#...#","#...#",".###."],
'5':["#####","#....","#....","#....",".###.","....#","....#","#...#",".###."],
"'":["#","#"],
'R':["####.","#...#","#...#","#...#","####.","#.#..","#..#.","#...#","#...#"],
'G':[".###.","#...#","#....","#....","#.###","#...#","#...#","#...#",".###."],
'U':["#...#","#...#","#...#","#...#","#...#","#...#","#...#","#...#",".###."],
'-':["..","..","..","..","##"],
}

FONT.update({
'1':[".#..","##..",".#..",".#..",".#..",".#..",".#..",".#..","####"],
'7':["#####","....#","...#.","...#.","..#..","..#..",".#...",".#...",".#..."],
'6':[".###.","#...#","#....","#....","####.","#...#","#...#","#...#",".###."],
'x':["...","...","...","...","#.#","#.#",".#.","#.#","#.#"],
})


FONT.update({
'T':["#####","..#..","..#..","..#..","..#..","..#..","..#..","..#..","..#.."],
'O':[".###.","#...#","#...#","#...#","#...#","#...#","#...#","#...#",".###."],
'0':[".###.","#...#","#...#","#...#","#...#","#...#","#...#","#...#",".###."],
'P':["####.","#...#","#...#","#...#","####.","#....","#....","#....","#...."],
'C':[".###.","#...#","#....","#....","#....","#....","#....","#...#",".###."],
'I':["###",".#.",".#.",".#.",".#.",".#.",".#.",".#.","###"],
'W':["#...#","#...#","#...#","#...#","#...#","#.#.#","#.#.#","##.##","#...#"],
'H':["#...#","#...#","#...#","#...#","#####","#...#","#...#","#...#","#...#"],
'2':[".###.","#...#","....#","...#.","..#..",".#...","#....","#....","#####"],
'9':[".###.","#...#","#...#","#...#",".####","....#","....#","#...#",".###."],
})
FONT.update({
'3':[".###.","#...#","....#","....#","..##.","....#","....#","#...#",".###."],
'4':["...#.","..##.",".#.#.","#..#.","#..#.","#####","...#.","...#.","...#."],
'L':["#....","#....","#....","#....","#....","#....","#....","#....","#####"],
})
def label(c,left,year):
    x=1
    for i,part in enumerate(left.split(' ')):
        x=c.text(x,31,part)+2
    c.text(c.w-2-c.width(year),31,year)

class Canvas:
    def __init__(s,w,h): s.w,s.h=w,h; s.px={}; s.ox=0; s.oy=0
    def p(s,x,y,c):
        x+=s.ox; y+=s.oy
        if 0<=x<s.w and 0<=y<s.h: s.px[(x,y)]=c
    def hl(s,x0,x1,y,c):
        for x in range(min(x0,x1),max(x0,x1)+1): s.p(x,y,c)
    def vl(s,x,y0,y1,c):
        for y in range(min(y0,y1),max(y0,y1)+1): s.p(x,y,c)
    def line(s,x0,y0,x1,y1,c):
        n=max(abs(x1-x0),abs(y1-y0))
        for i in range(n+1):
            s.p(round(x0+(x1-x0)*i/n),round(y0+(y1-y0)*i/n),c)
    def rect(s,x0,y0,x1,y1,c):
        s.hl(x0,x1,y0,c);s.hl(x0,x1,y1,c);s.vl(x0,y0,y1,c);s.vl(x1,y0,y1,c)
    def text(s,x,y,t,c='G',gap=1):
        ox,oy=s.ox,s.oy; s.ox=s.oy=0
        try: return s._text(x,y,t,c,gap)
        finally: s.ox,s.oy=ox,oy
    def _text(s,x,y,t,c='G',gap=1):
        for ch in t:
            if ch==' ': x+=3; continue
            g=FONT[ch]
            for dy,row in enumerate(g):
                for dx,v in enumerate(row):
                    if v=='#': s.p(x+dx,y+dy,c)
            x+=len(g[0])+gap
        return x
    def width(s,t,gap=1):
        return sum((3 if ch==' ' else len(FONT[ch][0])+gap) for ch in t)-gap
    def render(s):
        im=Image.new('RGBA',(s.w,s.h),(0,0,0,0));P=im.load()
        occ={}
        for (x,y),c in s.px.items(): occ[(x,y)]=('b',c)
        for (x,y),c in s.px.items():
            q=(x+1,y+1)
            if q not in occ and q[0]<s.w and q[1]<s.h: occ[q]=('d',c)
        # glow
        glow={}
        for (x,y),(k,c) in occ.items():
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    q=(x+dx,y+dy)
                    if q in occ or not(0<=q[0]<s.w and 0<=q[1]<s.h): continue
                    a=51 if (dx==0 or dy==0) else 30
                    col=BRIGHT[c] if k=='b' else DARK[c]
                    if q not in glow or glow[q][3]<a: glow[q]=col+(a,)
        for q,v in glow.items(): P[q]=v
        for (x,y),(k,c) in occ.items():
            P[x,y]=(BRIGHT[c] if k=='b' else DARK[c])+(255,)
        return im

# ---- shared naval base: band of waves along the bottom of the art area
import math
WAVE_TOP=25   # waves occupy rows 25-28; art sits above, label at 31
def naval_waves(c,style='sine',period=12,phase=0):
    W=c.w
    if style=='sine':
        prev=None
        for x in range(1,W-2):
            y=WAVE_TOP+round(1.5-1.5*math.sin(2*math.pi*(x+phase)/period))
            if prev is not None and abs(y-prev)>1: c.p(x,(y+prev)//2,'B')
            c.p(x,y,'B'); prev=y
    else:  # breaking crests: rise, curl forward, drop
        shape=[(0,28),(1,28),(2,27),(3,26),(4,25),(5,25),(6,25),(7,26),(6,26),(8,28),(9,28)]
        for x0 in range(1-phase,W-2,period):
            for dx,y in shape:
                if 1<=x0+dx<=W-3: c.p(x0+dx,y,'B')
