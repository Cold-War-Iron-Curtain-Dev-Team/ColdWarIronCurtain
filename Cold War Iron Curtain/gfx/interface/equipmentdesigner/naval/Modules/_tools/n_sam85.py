import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from draw import *
W=76; c=Canvas(W,42)
STYLE=sys.argv[2] if len(sys.argv)>2 else 'sine'
E=W-56
# missile (RIM-7M style), nose left
by=5; nx=6+E//2; tail=nx+44+E//2
c.p(nx,by+1,'W');c.p(nx+1,by+1,'W')
c.hl(nx+2,tail-12,by,'W'); c.hl(nx+1,tail-12,by+2,'W')
c.rect(tail-11,by,tail,by+2,'Y'); c.vl(tail-9,by,by+2,'Y')
wx=nx+18+E//4
for i in range(3):
    c.hl(wx-i,wx+2,by-1-i,'B'); c.hl(wx-i,wx+2,by+3+i,'B')
for i in range(3):
    c.hl(tail-3-i,tail-1,by-1-i,'B'); c.hl(tail-3-i,tail-1,by+3+i,'B')
# Mk29-style 8-cell box launcher, side view
lx0,lx1=4,W-6; ly0,ly1=13,20; mid=(ly0+ly1)//2
c.rect(lx0,ly0,lx1,ly1,'R'); c.hl(lx0,lx1,mid,'R')
for rx in (lx0+4,lx0+6,(lx0+lx1)//2-1,(lx0+lx1)//2+1,lx1-4): c.vl(rx,ly0,ly1,'R')
c.vl(lx0-2,ly0+1,mid-1,'B'); c.vl(lx0-2,mid+1,ly1-1,'B')
# trainable pedestal
cx=(lx0+lx1)//2
c.hl(cx-6,cx+6,ly1+1,'G'); c.line(cx-6,ly1+1,cx-8,23,'G'); c.line(cx+6,ly1+1,cx+8,23,'G')
naval_waves(c,STYLE)
c.text(1,31,"N-SAM"); c.text(W-2-c.width("'85"),31,"'85")
c.render().save(sys.argv[1])
