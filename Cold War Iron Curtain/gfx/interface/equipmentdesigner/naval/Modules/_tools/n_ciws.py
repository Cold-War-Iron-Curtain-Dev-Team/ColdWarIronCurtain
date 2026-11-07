# Mk 15 Phalanx CIWS, side view, firing left
import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from draw import *
c=Canvas(76,42)
# radome ("R2-D2" dome): straight sides, well-rounded crown
L,R=34,58
c.vl(L,8,15,'R'); c.vl(R,8,15,'R')
c.p(L+1,7,'R'); c.p(L+1,6,'R'); c.p(L+2,5,'R'); c.p(L+3,4,'R'); c.hl(L+4,L+5,3,'R'); c.hl(L+6,L+8,2,'R')
c.p(R-1,7,'R'); c.p(R-1,6,'R'); c.p(R-2,5,'R'); c.p(R-3,4,'R'); c.hl(R-5,R-4,3,'R'); c.hl(R-8,R-6,2,'R')
c.hl(L+9,R-9,1,'R')
c.hl(L+3,R-3,6,'R')                                 # search antenna band
c.rect(L-3,9,L,13,'R')                              # track antenna on the front face
# M61 gatling: barrel cluster, clamps, receiver
cy=19
for y in (cy-2,cy,cy+2): c.hl(8,33,y,'G'); c.p(6,y,'Y'); c.p(7,y,'Y')
c.rect(10,cy-4,12,cy+4,'B'); c.rect(22,cy-4,24,cy+4,'B')
c.rect(34,16,44,22,'B'); c.p(39,cy-1,'B'); c.p(38,cy,'B'); c.p(40,cy,'B'); c.p(39,cy+1,'B')
# ammunition drum
c.rect(45,16,60,22,'W')
for x in range(48,60,3): c.vl(x,17,21,'W')
c.vl(61,17,21,'W')
# training base
c.hl(36,60,23,'G'); c.line(36,23,33,26,'G'); c.line(60,23,63,26,'G'); c.hl(33,63,26,'G')
label(c,"1x CIWS","'85"); c.render().save(sys.argv[1])
