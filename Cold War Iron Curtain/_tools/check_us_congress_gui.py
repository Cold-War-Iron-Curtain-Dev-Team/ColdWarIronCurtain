"""Offline US Congress GUI audit using native textures, font metrics and installed trigger documentation.

Example: python _tools/check_us_congress_gui.py --game-dir "D:/SteamLibrary/steamapps/common/Hearts of Iron IV"
Diagnostic previews represent sample data, not a running game; shader tints are emulated.
"""
from pathlib import Path
import re
from generate_us_congress_overlays import PARTY_COLOURS, OVERLAY_COLOURS, OPACITY, generate, generate_shader, shader_path
R=Path(__file__).resolve().parents[1]
def read(rel):
 return (R/rel).read_bytes().decode('utf-8-sig').replace('\r\n','\n')
def end_block(s,opening):
 depth=0;quote=False;comment=False;escape=False
 for i in range(opening,len(s)):
  c=s[i]
  if comment:
   if c=='\n':comment=False
   continue
  if quote:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quote=False
   continue
  if c=='#':comment=True
  elif c=='"':quote=True
  elif c=='{':depth+=1
  elif c=='}':
   depth-=1
   if depth==0:return i+1
 raise AssertionError('Unbalanced block')
def decisions(s):
 clean=re.sub(r'"(?:\\.|[^"\\])*"|#[^\n]*',lambda m:' '*len(m[0]),s)
 depth=0;prev=0
 for m in re.finditer(r'(?m)^[ \t]*(\w+)\s*=\s*\{',clean):
  depth+=clean.count('{',prev,m.start())-clean.count('}',prev,m.start());prev=m.start()
  if depth==1:yield m.start(),end_block(s,m.end()-1),m[1]

# Run a strict syntax parser over all changed Congress files.
TOKEN=re.compile(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}=<>]|[^\s{}=<>]+')
def parse(s):
 tokens=[t for t in TOKEN.findall(s) if not t.startswith('#')];i=0
 def block(nested=False):
  nonlocal i
  items=[]
  while i<len(tokens):
   if tokens[i]=='}':
    assert nested,'Unexpected closing brace'
    i+=1;return items
   key=tokens[i];i+=1
   if i<len(tokens) and tokens[i] in ('=','<','>'):
    op=tokens[i];i+=1
    assert i<len(tokens),'Missing value'
    val=tokens[i];i+=1
    if val=='{':val=block(True)
    elif val=='}':raise AssertionError('Missing value before closing brace')
    if key.startswith('"'):key=key[1:-1]
    if isinstance(val,str) and val.startswith('"'):val=val[1:-1]
    items.append((key,op,val))
   else:items.append((key,None,None))
  assert not nested,'Unclosed block'
  return items
 return block()
files=['common/decisions/US_HOUSE.txt','common/scripted_effects/Initialization.txt','common/scripted_guis/Parliament.txt','common/scripted_guis/US_CONGRESS.txt','common/scripted_localisation/IC_localisation.txt','interface/WMD.gui','common/on_actions/USA_congress_gui_on_actions.txt','common/scripted_effects/USA_congress_gui_effects.txt','common/scripted_localisation/USA_congress_gui_localisation.txt','common/scripted_triggers/USA_congress_gui_triggers.txt','interface/US_Congress_Overview.gfx','interface/New_Technology.gfx','interface/US_Congress_State_Overlays.gfx']
trees={f:parse(read(f)) for f in files}
map_loc_file='common/scripted_localisation/USA_congress_map_localisation.txt'
trees[map_loc_file]=parse(read(map_loc_file))
lobby_loc_file='common/scripted_localisation/USA_congress_lobbying_localisation.txt'
trees[lobby_loc_file]=parse(read(lobby_loc_file))
vote_loc_file='common/scripted_localisation/USA_congress_vote_localisation.txt'
vote_effect_file='common/scripted_effects/USA_congress_vote_effects.txt'
trees[vote_loc_file]=parse(read(vote_loc_file))
trees[vote_effect_file]=parse(read(vote_effect_file))
trees['interface/US_Congress_Controls.gfx']=parse(read('interface/US_Congress_Controls.gfx'))
print('PASS: syntax parsed for',len(trees),'Congress files.')

from PIL import Image
import argparse
cli=argparse.ArgumentParser(description=__doc__)
cli.add_argument('--game-dir', type=Path, required=True, help='Installed Hearts of Iron IV directory')
cli.add_argument('--preview-dir', type=Path, help='Optionally write diagnostic PNGs')
args=cli.parse_args()
G=args.game_dir
assert (G/'hoi4.exe').exists(), 'Provide the installed game directory.'
def get(node,key,default=None):
 return next((v for k,o,v in node if k.lower()==key.lower()),default)
def named(nodes,name):
 return next(v for k,o,v in nodes if isinstance(v,list) and get(v,'name')==name)
def assets(kind,bases):
 index={}
 for base in bases:
  for p in (base/'interface').rglob('*.gfx'):
   s=p.read_text(encoding='utf-8-sig',errors='replace')
   for m in re.finditer(r'\b('+kind+r')\s*=\s*\{',s,re.I):
    try:node=parse(s[m.start():end_block(s,m.end()-1)])[0][2]
    except (AssertionError,IndexError):continue
    name=get(node,'name')
    if name:index[name]=node
 return index
sprites=assets('spriteType|textSpriteType|progressbarType|corneredTileSpriteType|bitmapfont',[G,R])
window=named(get(trees['interface/WMD.gui'],'guiTypes'),'US_CONGRESS_UI')
def tex_size(name):
 n=sprites.get(name)
 if not n:return None
 path=get(n,'texturefile');frames=float(get(n,'noOfFrames',1))
 size=get(n,'size')
 if isinstance(size,list):return (float(get(size,'x')),float(get(size,'y')))
 if path:
  for b in [R,G]:
   p=b/path.lstrip('/')
   if p.exists():
    with Image.open(p) as im:return (im.width/frames,im.height)
 size=get(n,'size')
 if size:return (float(get(size,'x')),float(get(size,'y')))

def get(node,key,default=None):
 return next((v for k,o,v in node if k.lower()==key.lower()),default)
def find_named(nodes,name):
 for k,o,v in nodes:
  if isinstance(v,list) and get(v,'name')==name:return v
 raise AssertionError('Missing named node '+name)
gui_tree=get(trees['common/scripted_guis/US_CONGRESS.txt'],'scripted_gui')
overview=get(gui_tree,'US_CONGRESS')
widgets=find_named(get(trees['interface/WMD.gui'],'guiTypes'),'US_CONGRESS_UI')
triggers={k:v for block,op,body in overview if block=='triggers' for k,op,v in body}
custom={k:v for k,o,v in trees['common/scripted_triggers/USA_congress_gui_triggers.txt']}
custom.update({k:v for k,o,v in parse(read('common/scripted_triggers/IC_state_decision_triggers.txt'))})
effects={k:v for k,o,v in trees['common/scripted_effects/Initialization.txt']}
effects.update({k:v for k,o,v in trees[vote_effect_file]})
loc_funcs={get(v,'name'):v for f in ['common/scripted_localisation/USA_congress_gui_localisation.txt','common/scripted_localisation/IC_localisation.txt',lobby_loc_file,vote_loc_file] for k,o,v in trees[f] if k=='defined_text'}
def resolve(value,env):
 if isinstance(value,(float,int)):return value
 if re.fullmatch(r'\d+\.id',value):return float(value[:-3])
 if value.startswith('token:'):return value.removeprefix('token:')
 bank=env.get('country_vars',env['vars']) if value.startswith('USA.') else env['vars']
 if value.startswith('USA.'):value=value[4:]
 if value=='days_decision_timeout@var:usa_current_legislation':return env.get('decision_timers',{}).get(bank.get('usa_current_legislation'),0)
 try:return float(value)
 except ValueError:return bank.get(value,0)
def compare(a,op,b):return {'=':lambda:a==b,'>':lambda:a>b,'<':lambda:a<b}[op]()
def test(node,env):
 def atom(k,o,v):
  if k=='OR':return any(atom(*item) for item in v)
  if k=='AND':return test(v,env)
  if k=='NOT':return not test(v,env)
  if k=='check_variable':return all(compare(resolve(key,env),op,resolve(value,env)) for key,op,value in v)
  if k in ('has_country_flag','has_global_flag'):return v in env['flags']
  if k=='has_variable':return v in env['vars']
  if k=='always':return v=='yes'
  if k=='tag':return v==env.get('tag','USA')
  if k=='is_ai':return (v=='yes')==env.get('ai',False)
  if k=='has_political_power':return compare(env['pp'],o,float(v))
  if k=='date':return compare(tuple(map(int,env['date'].split('.'))),o,tuple(map(int,v.split('.'))))
  if k=='has_country_leader':return get(v,'name')==env.get('leader')
  if k=='has_state_flag':return v in env.get('state_flags',set())
  if k.startswith('var:'):
   new=dict(env);new['country_vars']=env.get('country_vars',env['vars']);new['vars']=env.get('state_vars',{});return test(v,new)
  if k=='USA':
   new=dict(env);new['vars']=env.get('country_vars',env['vars']);return test(v,new)
  if k.isdigit():
   new=dict(env);new['country_vars']=env.get('country_vars',env['vars']);new['vars']={**env.get('state_vars',{}),'id':float(k)};return test(v,new)
  if k in custom:return test(custom[k],env)==(v=='yes')
  raise AssertionError('Unsupported trigger '+k)
 return all(atom(*item) for item in node)
def run(node,env):
 branch=None
 for k,o,v in node:
  if k in ('if','else_if','else'):
   if k=='if':branch=False
   if not branch and (k=='else' or test(get(v,'limit',[]),env)):
    run([(key,op,val) for key,op,val in v if key!='limit'],env);branch=True
   continue
  branch=None
  if k in ('add_to_variable','subtract_from_variable'):
   for key,op,value in v:env['vars'][key]=env['vars'].get(key,0)+(1 if k=='add_to_variable' else -1)*resolve(value,env)
  elif k=='set_variable':
   for key,op,value in v:env['vars'][key]=resolve(value,env)
  elif k=='set_country_flag':env['flags'].add(v)
  elif k=='clr_country_flag':env['flags'].discard(v)
  elif k=='clear_variable':env['vars'].pop(v,None)
  elif k=='add_political_power':env['pp']+=float(v)
  elif k=='clamp_variable':
   key=get(v,'var');env['vars'][key]=max(resolve(get(v,'min'),env),min(resolve(get(v,'max'),env),env['vars'].get(key,0)))
  elif k=='hidden_effect':run(v,env)
  elif k in effects:
   body=effects[k]
   if isinstance(v,list):
    parameters={key:value for key,op,value in v}
    def substitute(value):
     if isinstance(value,list):return [(substitute(key),op,substitute(val)) for key,op,val in value]
     if isinstance(value,str):return re.sub(r'\$(\w+)\$',lambda m:parameters[m[1]],value)
     return value
    body=substitute(body)
   run(body,env)
  else:raise AssertionError('Unsupported effect '+k)
def env(**kwargs):
 e={'vars':{},'flags':set(),'pp':100,'date':'1949.1.1','leader':'Harry S. Truman','tag':'USA'}
 e.update(kwargs);return e

from functools import lru_cache
from PIL import ImageDraw, ImageChops
loc={m[1]:m[2] for p in (R/'localisation/english').glob('*.yml') for m in re.finditer(r'(?m)^[ \t]*([^\s:#]+):\d*\s*"(.*)"\s*$',p.read_text(encoding='utf-8-sig'))}
@lru_cache(None)
def load_sprite(name,frame=1):
 node=sprites.get(name)
 assert node is not None,('Missing sprite',name)
 effect=get(node,'effectFile','')
 party=next((party for party in OVERLAY_COLOURS if effect==shader_path(party).relative_to(R).as_posix()),None)
 tex=get(node,'texturefile')
 if tex:
  for base in (R,G):
   path=base/tex.replace('\\','/').lstrip('/')
   if path.is_file():
    im=Image.open(path).convert('RGBA');frames=int(get(node,'noOfFrames',1));width=im.width//frames
    im=im.crop(((frame-1)*width,0,frame*width,im.height))
    if party:
     # Reproduce the generated native sprite shader tint.
     rgb=OVERLAY_COLOURS[party]
     alpha=im.getchannel('A').point(lambda a:round(a*OPACITY))
     im=Image.new('RGBA',im.size,rgb+(0,));im.putalpha(alpha)
    size=get(node,'size');border=get(node,'borderSize')
    if isinstance(size,list) and border:
     w,h=int(get(size,'x')),int(get(size,'y'));bx=int(get(border,'x'));by=int(get(border,'y'))
     resized=Image.new('RGBA',(w,h));sx=[0,bx,im.width-bx,im.width];sy=[0,by,im.height-by,im.height];dx=[0,bx,w-bx,w];dy=[0,by,h-by,h]
     for row in range(3):
      for col in range(3):
       tile=im.crop((sx[col],sy[row],sx[col+1],sy[row+1])).resize((dx[col+1]-dx[col],dy[row+1]-dy[row]))
       resized.alpha_composite(tile,(dx[col],dy[row]))
     im=resized
    return im
 size=get(node,'size')
 if size:return Image.new('RGBA',(int(get(size,'x')),int(get(size,'y'))),(0,0,0,0))
 raise AssertionError(('Missing texture',name,tex))
@lru_cache(None)
def font_data(name):
 entry=sprites.get(name);path=(get(entry,'path') or get(entry,'fontfiles',[(chr(34)+'gfx/fonts/'+name+chr(34),None,None)])[0][0].strip(chr(34))) if entry else 'gfx/fonts/'+name
 fnt=None;atlas=None
 for base in (R,G):
  p=base/(path+'.fnt')
  if p.exists():
   fnt=p.read_text(encoding='utf-8-sig');break
 assert fnt,('Missing font',name,path)
 for base in (R,G):
  p=base/(path+'.dds')
  if p.exists():atlas=Image.open(p).convert('RGBA');break
 assert atlas is not None,name
 chars={}
 for line in fnt.splitlines():
  if line.startswith('char '):
   row={k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',line)};chars[row['id']]=row
 height=int(re.search(r'\blineHeight=(\d+)',fnt)[1])
 return chars,height,atlas
def advance(font,text):
 chars,_,_=font_data(font)
 return sum(chars.get(ord(c),chars.get(63))['xadvance'] for c in text)
def wrapped(font,text,width):
 lines=[]
 for paragraph in text.split('\n'):
  line=''
  for word in paragraph.split(' '):
   candidate=(line+' '+word).strip()
   if line and advance(font,candidate)>width:lines.append(line);line=word
   else:line=candidate
  lines.append(line)
 return lines
def select_func(name,e):
 for k,o,v in loc_funcs[name]:
  if k=='text' and test(get(v,'trigger',[]),e):return get(v,'localization_key')
 return ''
def expand(value,e,depth=0):
 if depth>10:return value
 value=loc.get(value,value)
 value=re.sub(r'\$([\w.]+)\$',lambda m:loc.get(m[1],m[1]),value)
 value=value.replace('\\n','\n')
 def variable(m):
  raw=m[1].split('|')[0]
  if raw.endswith('.GetTokenLocalizedKey'):
   key=raw.removesuffix('.GetTokenLocalizedKey').removeprefix('USA.')
   return loc.get(e['vars'].get(key,''),'')
  v=resolve(raw,e)
  return str(int(v)) if isinstance(v,(float,int)) else str(v)
 value=re.sub(r'\[\?([^\]]+)\]',variable,value)
 def function(m):
  name=m[1]
  overrides={'GetCurrentUSStateName':'California','GetNextElectionYear':'1952','GetStateUnionLevel':'High','GetStateBlackPopLevel':'12%','GetStateEthnicWhiteLevel':'25%','GetStateJewishLevel':'3%','GetStateCollegeLevel':'20%','GetStateContestType':'Primary','GetDemAllocationMethod':'Proportional'}
  if name in overrides:return overrides[name]
  if name in loc_funcs:return expand(select_func(name,e),e,depth+1)
  return '...'
 value=re.sub(r'\[([^\]]+)\]',function,value)
 value=re.sub(chr(167)+'.','',value)
 return value
def visibility(name,e):
 rule=triggers.get(name+'_visible')
 return True if rule is None else test(rule,e)
def rect(n,image=None):
 pos=get(n,'position',[]);x=float(get(pos,'x',0));y=float(get(pos,'y',0))
 if image is not None:w,h=image.size
 else:w,h=float(get(n,'maxWidth',0)),float(get(n,'maxHeight',0))
 scale=float(get(n,'scale',1))
 return (x,y,w*scale,h*scale)
def overlaps(a,b):
 x,y,w,h=a;X,Y,W,H=b
 return x<X+W and X<x+w and y<Y+H and Y<y+h
def paint_text(canvas,n,text):
 x,y,w,h=rect(n);font=get(n,'font');lines=wrapped(font,text,w);chars,lineheight,atlas=font_data(font)
 for row,line in enumerate(lines):
  px=x+(w-advance(font,line))/2 if get(n,'format')=='center' else x
  for c in line:
   glyph=chars.get(ord(c),chars.get(63));gx,gy=round(px+glyph['xoffset']),round(y+row*lineheight+glyph['yoffset'])
   crop=atlas.crop((glyph['x'],glyph['y'],glyph['x']+glyph['width'],glyph['y']+glyph['height']))
   canvas.alpha_composite(crop,(gx,gy));px+=glyph['xadvance']
 return len(lines)*lineheight
audit_dir=args.preview_dir
if audit_dir:audit_dir.mkdir(parents=True,exist_ok=True)
from generate_us_congress_votes import bill_metadata, arguments, instrument, generate as generate_votes
bill_source=read('common/decisions/US_HOUSE.txt');vote_bills=bill_metadata(bill_source)
properties={k:v for kind,o,body in overview if kind=='properties' for k,o,v in body}
for mode,selected,label in [(0,0,'overview'),(0,378,'state'),(1,378,'general'),(2,378,'primary'),(0,0,'democratic_states'),(0,0,'republican_states'),(0,0,'lobby_result'),(0,378,'lobby_result_state'),(0,0,'votes_needed'),(0,0,'last_vote_failed'),(0,0,'unavailable'),(0,0,'no_bill'),(0,0,'veto_vote')]:
 variables={'show_usa_congress_alt':mode,'USA_SEN_POL_DETAILS':selected,'dem_house_caucus':263,'gop_house_caucus':172,'senate_dem_caucus':55,'senate_gop_caucus':41,'supseat':218,'US_HOUSE_SIZE':435,'supseat_sen':55,'US_SENATE':96,'moderate_dem':30,'progressive_dem':7,'dixiecrat_dem':18,'moderate_gop':16,'conservative_gop':9,'liberal_gop':16,'Dem_Canidates^num':3,'usa_current_legislation':'The_Price_Anderson_Nuclear_Industries_Indemnity_Act'}
 if label.startswith('lobby_result'):variables.update(usa_lobby_result_target=1,usa_lobby_result_votes=30)
 variables.update(usa_current_legislation_short='USA_CONGRESS_SHORT_'+variables['usa_current_legislation'],usa_vote_house_required=217,usa_vote_senate_required=48,usa_vote_house_needed=0,usa_vote_senate_needed=0)
 variables.update(usa_last_bill_result=2 if label=='last_vote_failed' else 1,usa_last_bill=vote_bills[0]['key'],usa_last_bill_short=vote_bills[0]['short_key'],usa_last_house_support=280,usa_last_senate_support=72,usa_last_house_total=435,usa_last_senate_total=96,usa_last_house_required=217,usa_last_senate_required=48)
 if label=='votes_needed':variables.update(supseat=190,supseat_sen=40,usa_vote_house_needed=27,usa_vote_senate_needed=8)
 if label=='last_vote_failed':variables.update(usa_last_house_support=190,usa_last_senate_support=40)
 if label=='veto_vote':
  veto=next(bill for bill in vote_bills if bill['house']==292)
  variables.update(usa_current_legislation=veto['key'],usa_current_legislation_short=veto['short_key'],supseat=220,supseat_sen=50,usa_vote_house_required=292,usa_vote_senate_required=67,usa_vote_house_needed=72,usa_vote_senate_needed=17)
 senators=(1,1) if label=='democratic_states' else (2,2) if label=='republican_states' else (1,2)
 e=env(vars=variables,state_vars={'senator^0':senators[0],'senator^1':senators[1],'d_pvi':0,'r_pvi':0},flags={'law_passing','moderate_dem_sup','progressive_dem_sup'})
 e['decision_timers']={variables['usa_current_legislation']:23}
 if label=='unavailable':e['pp']=49
 if label=='no_bill':
  run(effects['clear_support_types'],e);e['flags'].discard('law_passing')
  e['vars']={key:value for key,value in e['vars'].items() if not key.startswith('usa_last_')}
  e['vars'].update(supseat=0,supseat_sen=0)
 canvas=Image.new('RGBA',(1000,600),(0,0,0,255));buttons=[];texts=[];cards=[];warnings=[]
 for kind,o,n in window:
  if not isinstance(n,list):continue
  name=get(n,'name')
  if not name or not visibility(name,e):continue
  if kind.lower() in ('icontype','buttontype','background'):
   sprite=get(n,'spriteType',get(n,'quadTextureSprite'))
   if not sprite:continue
   image=get(properties.get(name,[]),'image')
   if image:sprite=expand(image,e)
   im=load_sprite(sprite,int(get(n,'frame',1)));x,y,w,h=rect(n,im)
   if not (0<=x and 0<=y and x+w<=1000 and y+h<=600):warnings.append(('outside window',name,(x,y,w,h)))
   if get(n,'scale') is not None:im=im.resize((round(w),round(h)))
   canvas.alpha_composite(im,(round(x),round(y)))
   if kind.lower()=='buttontype':
    buttons.append((name,(x,y,w,h)))
    labeltext=get(n,'buttonText')
    if labeltext:
     font=get(n,'buttonFont','hoi_16mbs');text=expand(labeltext,e);tw=advance(font,text)
     if tw>w-8:warnings.append(('button text too wide',name,text,tw,w))
     textnode=[('position','=',[('x','=',str(x)),('y','=',str(y+(h-font_data(font)[1])/2))]),('font','=',font),('format','=','center'),('maxWidth','=',str(w)),('maxHeight','=',str(h))]
     paint_text(canvas,textnode,text)
   if name.startswith('speaker_') or name=='vp_portrait_border':cards.append((name,(x,y,w,h)))
  elif kind.lower()=='instanttextboxtype':
   raw=get(n,'text','')
   if re.fullmatch('[A-Z][A-Z0-9_]+',raw):assert raw in loc,('Missing displayed localisation',name,raw)
   text=expand(raw,e);font=get(n,'font');r=rect(n)
   height=paint_text(canvas,n,text)
   if height>r[3]:warnings.append(('text too tall',name,text,height,r[3]))
   if r[0]<0 or r[1]<0 or r[0]+r[2]>1000 or r[1]+r[3]>600:warnings.append(('text outside window',name,r))
   texts.append((name,r))
 for card,cr in cards:
  for button,br in buttons:
   if overlaps(cr,br):warnings.append(('card/button collision',card,button))
 for i,(name,r) in enumerate(buttons):
  if name.endswith('_poli_details'):continue
  for other,other_r in buttons[i+1:]:
   if not other.endswith('_poli_details') and overlaps(r,other_r):warnings.append(('button collision',name,other))
 for i,(name,r) in enumerate(texts):
  for button,br in buttons:
   if name.startswith('congress_legend_') and button.endswith('_poli_details'):continue
   if overlaps(r,br):warnings.append(('text/button collision',name,button))
  for other,other_r in texts[i+1:]:
   if overlaps(r,other_r):warnings.append(('text collision',name,other))
 if audit_dir:canvas.convert('RGB').save(audit_dir/(label+'.png'))
 assert not warnings,(label,warnings)
 print('PASS: native assets, text metrics and control collisions in',label)

billnode=next(n for kind,o,n in window if isinstance(n,list) and get(n,'name')=='LEGISLATION')
tall=[]
bill_source=read('common/decisions/US_HOUSE.txt')
for bill in vote_bills:
 e=env(vars={'usa_current_legislation':bill['key'],'usa_current_legislation_short':bill['short_key']},flags={'law_passing'})
 text=expand('[GetUSACongressCurrentBillCompact]',e)
 height=len(wrapped(get(billnode,'font'),text,float(get(billnode,'maxWidth'))))*font_data(get(billnode,'font'))[1]
 if height>float(get(billnode,'maxHeight')):tall.append((bill['key'],height))
assert not tall,tall
print('PASS: all 517 bill names fit using actual font metrics.')

# Each state setup must write to the same representative IDs used by the map.
representatives={}
for key,op,value in get(overview,'effects'):
 if key.endswith('_poli_details_click'):
  selected=get(get(value,'set_variable',[]),'USA_SEN_POL_DETAILS')
  assert selected and selected.endswith('.id'),('State selection',key)
  representatives[key.removesuffix('_poli_details_click')]=int(selected.removesuffix('.id'))
assert len(representatives)==52
setup_count=0
for key,op,value in trees['common/scripted_effects/Initialization.txt']:
 match=re.fullmatch('senate_pvi_set_(\\d+)',key)
 if not match:continue
 year=int(match[1]);states=[int(k) for k,o,v in value if k.isdigit()]
 expected=set(representatives.values())
 if year<1960:expected-={463,629}
 assert len(states)==len(set(states)),('Duplicate PVI state',key)
 assert set(states)==expected,('PVI state IDs',key,'missing',expected-set(states),'unexpected',set(states)-expected)
 for state_id,op,state in value:
  if not state_id.isdigit():continue
  lean={k:v for name,o,values in state if name=='set_variable' for k,o,v in values}
  assert {'d_pvi','r_pvi'}<=lean.keys(),('Incomplete state lean',key,state_id)
  assert all(0<=float(lean[k])<=1 for k in ('d_pvi','r_pvi')),('PVI units',key,state_id)
 setup_count+=1
assert setup_count==13
print('PASS: all 13 partisan-lean setups use the correct state IDs and percentage units.')

# A syntax-only parser cannot validate trigger names. Use the installed game's registry.
doc=(G/'documentation/triggers_documentation.md').read_text(encoding='utf-8-sig')
builtins={x.lower() for x in re.findall(r'^## (\w+)',doc,re.M)}
registered=set()
for path in (R/'common/scripted_triggers').glob('*.txt'):
 try:registered.update(k for k,o,v in parse(path.read_text(encoding='utf-8-sig')))
 except AssertionError:registered.update(re.findall(r'^(\w+)\s*=\s*\{',path.read_text(encoding='utf-8-sig'),re.M))
def validate_conditions(node):
 for key,op,value in node:
  group=key.lower() in ('and','or','not','if','else_if','else','limit')
  scope=key.startswith('var:') or key.isdigit() or re.fullmatch('[A-Z]{3}',key) or key in ('ROOT','PREV','FROM','THIS')
  if group or scope:
   if isinstance(value,list):validate_conditions(value)
  else:assert key.lower() in builtins or key in registered,('Unregistered trigger',key)
for key,rule in triggers.items():validate_conditions(rule)
for key,rule in custom.items():
 if key.startswith('USA_congress_'):validate_conditions(rule)
assert sum(k=='triggers' for k,o,v in overview)==1
print('PASS: trigger names checked against installed game documentation; one consolidated overview trigger section.')

# Check every Speaker and VP alternative, including assets that are hidden in the sample previews.
by_name={get(v,'name'):v for k,o,v in window if isinstance(v,list) and get(v,'name')}
for name,node in by_name.items():
 if name.startswith('speaker_'):
  assert get(node,'scale') is None,('Unnecessary card scaling',name)
  assert load_sprite(get(node,'spriteType')).size==(172,258),name
  assert rect(node,load_sprite(get(node,'spriteType')))==(814,44,172,258),name
for name in sprites:
 if name.startswith('GFX_USA_congress_vp_'):assert load_sprite(name).size==(156,210),name
ordering=[get(v,'name') for k,o,v in window if isinstance(v,list)]
assert ordering.index('vp_leader_frame')<ordering.index('vp_portrait_border')<ordering.index('VP_Leader_Name')
assert get(by_name['vp_portrait_border'],'spriteType')=='GFX_pol_leader_frame'
for name in ('VP_Leader_Name','Speaker_Name'):
 font=get(by_name[name],'font')
 assert font_data(font)[1]<=float(get(by_name[name],'maxHeight'))
for function,caption in [('GetUSACongressVPName','VP_Leader_Name'),('SPEAKER_TITLE','Speaker_Name')]:
 node=by_name[caption];font=get(node,'font')
 for kind,op,entry in loc_funcs[function]:
  if kind!='text':continue
  text=loc.get(get(entry,'localization_key'),get(entry,'localization_key'))
  assert len(wrapped(font,text,float(get(node,'maxWidth'))))*font_data(font)[1]<=float(get(node,'maxHeight')),('Nameplate overflow',text)
for name,node in by_name.items():
 if name.endswith('_supported'):
  parent=by_name[name.removesuffix('_supported')]
  assert rect(node,load_sprite(get(node,'spriteType')))==rect(parent,load_sprite(get(parent,'quadTextureSprite')))
  assert get(node,'alwaystransparent')=='yes'
print('PASS: nine native Speaker cards, every VP portrait, nameplate layering and checkbox hit areas.')

# Lobbying behavior still needs to match the confirmation UI.
factions=['moderate_dem','progressive_dem','dixiecrat_dem','moderate_gop','conservative_gop','liberal_gop']
for choice,faction in enumerate(factions,1):
 e=env(vars={'lobby_check':choice,faction:13,'supseat_sen':5},flags={'law_passing'})
 run(effects['lobbying_effect'],e)
 assert e['pp']==50 and e['vars']['supseat_sen']==18 and faction+'_sup' in e['flags']
 run(effects['lobbying_effect'],e)
 assert e['pp']==50 and e['vars']['supseat_sen']==18
for power,flags in [(49.5,{'law_passing'}),(100,set())]:
 e=env(vars={'lobby_check':1,'moderate_dem':13,'supseat_sen':5},flags=flags,pp=power)
 run(effects['lobbying_effect'],e)
 assert e['pp']==power and e['vars']['supseat_sen']==5
for mode in (0,1,2):
 e=env(vars={'show_usa_congress_alt':mode,'USA_SEN_POL_DETAILS':378})
 for name in ('state_dem_campaign','state_dem_launch_newspaper_ads','state_dem_launch_radio_ads','state_dem_launch_television_ads','state_dem_invest_in_local_campaign','state_action_fundraise'):
  assert visibility(name,e)==(mode==2),(mode,name)
print('PASS: campaign controls are excluded from Congress; lobbying charges once and rejects stale/repeat purchases.')

# The lobbying dialog has a separate window and uses bottom-anchored buttons.
modal=find_named(get(trees['interface/WMD.gui'],'guiTypes'),'US_CONGRESS_UI_LOBBYING')
for choice in (1,2,3,4,5,6,10):
 e=env(vars={'lobby_check':choice,**{faction:13 for faction in factions},'supseat':190,'supseat_sen':40,'US_SENATE':96,'US_HOUSE_SIZE':435},flags={'law_passing'})
 canvas=Image.new('RGBA',(527,315));labels=[];buttons=[]
 for kind,o,node in modal:
  if not isinstance(node,list):continue
  name=get(node,'name');node=list(node)
  if get(node,'Orientation')=='LOWER_LEFT':
   position=get(node,'position')
   node=[(k,o,v) for k,o,v in node if k!='position']+[('position','=',[(k,o,str(float(v)+315) if k=='y' else v) for k,o,v in position])]
  if kind.lower() in ('buttontype','background'):
   sprite=get(node,'quadTextureSprite');image=load_sprite(sprite)
   x,y,w,h=rect(node,image)
   assert x>=0 and y>=0 and x+w<=527 and y+h<=315,('Dialog image bounds',name)
   canvas.alpha_composite(image,(round(x),round(y)))
   if kind.lower()=='buttontype':
    buttons.append((name,(x,y,w,h)))
    text=expand(get(node,'buttonText'),e);font=get(node,'buttonFont')
    assert advance(font,text)<=w-8,('Dialog button label',name,text)
  elif kind.lower()=='instanttextboxtype':
   text=expand(get(node,'text'),e);font=get(node,'font')
   x,y,w,h=rect(node)
   assert x>=0 and y>=0 and x+w<=527 and y+h<=315,('Dialog text bounds',name)
   assert paint_text(canvas,node,text)<=h,('Dialog text overflow',choice,name)
   labels.append((name,(x,y,w,h)))
 for name,r in labels:
  for button,br in buttons:assert not overlaps(r,br),('Dialog text/control collision',choice,name,button)
 if audit_dir and choice==1:canvas.convert('RGB').save(audit_dir/'lobbying.png')
print('PASS: all seven lobbying dialog variants fit above their buttons.')


# All party colours share silhouettes through native sprite-compatible shaders.
generated=R/'interface/US_Congress_State_Overlays.gfx'
assert generated.read_text(encoding='utf-8')==generate(), 'Regenerate Congress overlays.'
colour_names=[]
by_state={}
for name,node in sprites.items():
 if name.startswith('GFX_USA_legend_'):continue
 if get(node,'effectFile','') not in {shader_path(party).relative_to(R).as_posix() for party in OVERLAY_COLOURS}:continue
 colour_names.append(name)
 party,state=re.fullmatch(r'GFX_(DEM|GOP|SPLIT|AIP|NEUTRAL)_(.+)',name).groups()
 mask=get(node,'texturefile')
 assert '/Democratic_States/' in mask,('Unexpected state mask',name)
 assert get(node,'textureFile1') is None and get(node,'textureFile2') is None,('Progress-bar texture binding in sprite',name)
 assert get(node,'effectFile')==shader_path(party).relative_to(R).as_posix()
 assert get(node,'noOfFrames')=='1',('Unexpected sprite frames',name)
 assert get(node,'transparencecheck','no')!='yes',('Decorative DXT5 masks must not request CPU hit testing',name)
 by_state.setdefault(state,set()).add(mask)
 image=load_sprite(name)
 visible=sorted(((count,color) for count,color in image.getcolors(1<<20) if color[3]>0),reverse=True)
 assert visible,('Empty state overlay',name)
 assert visible[0][1][:3]==OVERLAY_COLOURS[party],('Incorrect party colour',name,visible[0][1])
 with Image.open(R/mask) as original:
  assert original.getchannel('A').getbbox()==image.getchannel('A').getbbox(),('Mask silhouette changed',name)
assert len(colour_names)==252 and len(by_state)==52
assert all(len(paths)==1 for paths in by_state.values()), 'Colour variants must reuse one mask.'
generated_nodes=get(parse(generated.read_text(encoding='utf-8')),'spriteTypes')
assert len(generated_nodes)==252 and all(kind=='spriteType' for kind,o,node in generated_nodes)
for party in OVERLAY_COLOURS:
 shader=shader_path(party).read_text(encoding='utf-8')
 assert shader==generate_shader(party)
 for declaration in ('VertexStruct VS_OUTPUT','BlendState BlendState','Effect Up','Effect Down','Effect Over','Effect Disable'):
  assert re.search(re.escape(declaration)+r'\s*\{',shader),('Invalid shader declaration',declaration)
 assert '"buttonstate.fxh"' in shader and 'v.vTexCoord + Offset' in shader
 assert 'ConstantBuffer' not in shader and 'TextureTwo' not in shader
print('PASS: 252 native sprites reuse 52 masks without unsupported DXT5 hit testing.')
# Reproduce the actual Texas delegation from the initial country history.
history=parse(read('history/countries/USA - United States.txt'))
texas=get(get(history,'1949.1.1'),'375')
texas_senators={k:float(v) for name,o,values in texas if name=='set_variable' for k,o,v in values if k.startswith('senator^')}
assert texas_senators
texas_env=env(vars={'show_usa_congress_alt':0},state_vars=texas_senators)
assert visibility('DEM_Texas',texas_env)
assert not visibility('GOP_Texas',texas_env) and not visibility('SPLIT_Texas',texas_env)
# Delegation colours must be exclusive, and a state with no senators is unfilled.
for senators,expected in [({},None),({'senator^0':1,'senator^1':1},'DEM'),({'senator^0':2,'senator^1':2},'GOP'),({'senator^0':1,'senator^1':2},'SPLIT')]:
 state_env=env(vars={'show_usa_congress_alt':0},state_vars=senators)
 visible=[party for party in ('DEM','GOP','SPLIT') if visibility(party+'_Texas',state_env)]
 assert visible==([expected] if expected else []),(senators,visible)
print('PASS: Texas matches its history and delegation colours are exclusive.')

# Verify the actual map widgets and historical delegations, including all insets.
from generate_us_congress_tooltips import STATES, generate as generate_tooltips, LOCALISATION, SCRIPTED_LOC
import json
expected_loc,expected_scripted=generate_tooltips()
assert LOCALISATION.read_text(encoding='utf-8-sig')==expected_loc
assert LOCALISATION.read_bytes().startswith(b'\xef\xbb\xbf'), 'Localisation YAML needs its UTF-8 BOM.'
assert not SCRIPTED_LOC.read_bytes().startswith(b'\xef\xbb\xbf'), 'A BOM prevents the game loading the scripted tooltip functions.'
assert SCRIPTED_LOC.read_text(encoding='utf-8')==expected_scripted
map_functions={get(v,'name'):v for k,o,v in trees[map_loc_file] if k=='defined_text'}
loc_funcs.update(map_functions)
actual_history=get(history,'1949.1.1')
map_widget_names={get(node,'spriteType'):name for name,node in by_name.items() if get(node,'spriteType')}
map_strings={line.split(':0 ',1)[0].strip():json.loads(line.split(':0 ',1)[1]) for line in expected_loc.splitlines() if ':0 ' in line}
for state in STATES:
 abbr,sid=state['abbr'],state['id']
 suffix={'CT':'Conneticut','DC':'DC','PR':'PR'}.get(abbr,state['name'].replace(' ','_'))
 key=f'USA_CONGRESS_MAP_{abbr}_TT'
 hits=[n for k,o,n in window if isinstance(n,list) and get(n,'pdx_tooltip')==key]
 assert len(hits)==1,('Missing or duplicate hover region',state['name'])
 click=get(get(overview,'effects'),get(hits[0],'name')+'_click')
 assert get(get(click,'set_variable'),'USA_SEN_POL_DETAILS')==sid+'.id',('Hover/click state mismatch',state['name'])
 raw=map_strings[key]
 assert f'[{sid}.GetUSACongressHoverDelegation]' in raw
 assert 'USA_SEN_MAP_TARGET' not in raw and 'USA_SEN_POL_DETAILS' not in raw
 if abbr!='OR':assert chr(167)+'Y"'+state['motto']+'"'+chr(167)+'!' in raw
 for party in (('NEUTRAL',) if abbr in ('DC','PR') else ('DEM','GOP','SPLIT','AIP','NEUTRAL')):
  assert 'GFX_'+party+'_'+suffix in map_widget_names,('Missing colour widget',party,state['name'])
 state_history=get(actual_history,sid,[])
 values={k:float(v) for name,o,body in state_history if name=='set_variable' for k,o,v in body if k.startswith('senator^')}
 state_env=env(vars={'show_usa_congress_alt':0},state_vars=values)
 fills=[party for party in ('DEM','GOP','SPLIT','NEUTRAL') if 'GFX_'+party+'_'+suffix in map_widget_names and visibility(map_widget_names['GFX_'+party+'_'+suffix],state_env)]
 assert len(fills)==1,('Black or overlapping state in 1949',state['name'],fills,values)
 if abbr in ('AK','HI','PR','DC'):assert fills==['NEUTRAL'],(abbr,fills)

for suffix,sid in [('Alaska',463),('Hawaii',629)]:
 for statehood in (False,True):
  state_env=env(vars={'show_usa_congress_alt':0},state_vars={'senator^1':1,'senator^2':2},flags={'ak_hi_state'} if statehood else set())
  fills=[party for party in ('DEM','GOP','SPLIT','NEUTRAL') if visibility(party+'_'+suffix,state_env)]
  assert fills==(['SPLIT'] if statehood else ['NEUTRAL']),('Statehood colour transition',suffix,statehood,fills)
for sid,flags,senators,want in [(367,set(),{'senator^1':1,'senator^2':1},'DEM'),(463,set(),{},'TERRITORY'),(629,set(),{},'TERRITORY'),(686,set(),{},'TERRITORY'),(1200,set(),{},'DC'),(463,{'ak_hi_state'},{'senator^1':1,'senator^2':2},'SPLIT')]:
 e=env(vars={'id':float(sid),**senators},flags=flags,country_vars={'show_usa_congress_alt':0})
 assert select_func('GetUSACongressHoverDelegation',e)=='USA_CONGRESS_HOVER_'+want
for date,want in [('1949.1.1','ORIGINAL_OR'),('1960.1.1','UNION_OR'),('1988.1.1','ORIGINAL_OR')]:
 assert select_func('GetUSACongressOregonMotto',env(date=date))=='USA_CONGRESS_MOTTO_'+want
print('PASS: all 52 historical map regions have one fill and a correctly scoped motto tooltip; statehood transitions work.')

# Event prose still calls GetCurrentVP. It must resolve the same ticket as Congress.
legacy_vp=find_named(parse(read('common/scripted_localisation/USA_Cabinet_Members_Scripted_Localization.txt')),'GetCurrentVP')
assert [(k,o,v) for k,o,v in legacy_vp if k!='name']==[(k,o,v) for k,o,v in loc_funcs['GetUSACongressVPName'] if k!='name']
loc_funcs['GetCurrentVP']=legacy_vp
for leader,date,flags,want in [
 ('Harry S. Truman','1949.1.1',set(),'USA_CONGRESS_VP_ALBEN_BARKLEY'),
 ('Dwight D. Eisenhower','1954.1.1',set(),'USA_CONGRESS_VP_RICHARD_NIXON'),
 ('Ronald Reagan','1981.1.20',{'Reagan80'},'USA_CONGRESS_VP_GEORGE_H_W_BUSH'),
 ('Jack Kemp','1989.1.20',{'Kemp88'},'USA_CONGRESS_VP_GEORGE_H_W_BUSH'),
]:
 assert select_func('GetCurrentVP',env(leader=leader,date=date,flags=flags))==want,('Legacy VP callback',leader,date)
print('PASS: legacy VP names resolve correctly for early Cold War and alternate presidential tickets.')

# Portraits and nameplates must expose the same complete officeholder tooltip.
for name,node in by_name.items():
 if name.startswith('speaker_') or name=='Speaker_Name':
  assert get(node,'pdx_tooltip')=='USA_CONGRESS_SPEAKER_TT',('Inconsistent Speaker tooltip',name)
for name in ('vp_leader_frame','vp_portrait_border','VP_Leader_Name'):
 assert get(by_name[name],'pdx_tooltip')=='USA_CONGRESS_VP_TT',('Inconsistent VP tooltip',name)
vp_name=loc_funcs['GetUSACongressVPName'];vp_desc=loc_funcs['GetUSACongressVPDescription']
names=[v for k,o,v in vp_name if k=='text'];descs=[v for k,o,v in vp_desc if k=='text']
assert len(names)==len(descs)==42
for name,desc in zip(names,descs):
 assert get(name,'trigger')==get(desc,'trigger'), 'VP biography selector diverges from the displayed name.'
 assert get(desc,'localization_key')==get(name,'localization_key')+'_DESC'
 key=get(desc,'localization_key');assert key in loc,('Missing officeholder biography',key)
 text=expand(key,env());assert len(text)>50 and '...' not in text,('Empty or unresolved biography',key)
name_rows=[v for k,o,v in loc_funcs['SPEAKER_TITLE'] if k=='text']
desc_rows=[v for k,o,v in loc_funcs['GetUSACongressSpeakerDescription'] if k=='text']
assert len(name_rows)==len(desc_rows)==10
for name,desc in zip(name_rows,desc_rows):
 assert get(name,'trigger')==get(desc,'trigger'), 'Speaker biography selector diverges from the displayed name.'
 key=get(desc,'localization_key');assert key in loc and len(expand(key,env()))>50,('Missing Speaker biography',key)
def officeholder_template(value):
 for token in ('[GetUSACongressVPName]','[SPEAKER_TITLE]'):value=value.replace(token,'{name}')
 for token in ('[GetUSACongressVPDescription]','[GetUSACongressSpeakerDescription]'):value=value.replace(token,'{description}')
 for token in ('Vice President of the United States','Speaker of the House of Representatives'):value=value.replace(token,'{office}')
 return value
assert officeholder_template(loc['USA_CONGRESS_VP_TT'])==officeholder_template(loc['USA_CONGRESS_SPEAKER_TT'])
officer_loc=R/'localisation/english/US_Congress_Officeholders_l_english.yml'
assert officer_loc.read_bytes().startswith(b'\xef\xbb\xbf')
assert not (R/'common/scripted_localisation/USA_congress_gui_localisation.txt').read_bytes().startswith(b'\xef\xbb\xbf')
print('PASS: VP and Speaker tooltips share one layout with a matching name and biography for every officeholder.')

# Lobbying must explain the same guards used by the transaction, and report only success.
from generate_us_congress_lobbying import FACTIONS, generate as generate_lobbying, LOCALISATION as LOBBY_LOC, SCRIPTED_LOC as LOBBY_SCRIPT
expected_loc,expected_script=generate_lobbying()
assert LOBBY_LOC.read_text(encoding='utf-8-sig')==expected_loc
assert LOBBY_SCRIPT.read_text(encoding='utf-8')==expected_script
assert LOBBY_LOC.read_bytes().startswith(b'\xef\xbb\xbf')
assert not LOBBY_SCRIPT.read_bytes().startswith(b'\xef\xbb\xbf')
for choice,code,label,faction,button,caption in FACTIONS:
 key='USA_CONGRESS_LOBBY_'+code+'_TT'
 for widget in (button,caption,button+'_supported'):
  assert get(by_name[widget],'pdx_tooltip')==key,('Missing lobbying tooltip hit area',widget)
 assert get(by_name[button],'quadTextureSprite')=='GFX_checkbox_small4'
 assert get(by_name[button+'_supported'],'frame')=='2'
 assert get(by_name[button+'_supported'],'alwaystransparent')=='yes'
 function='GetUSACongressLobby'+code.replace('_','')+'Status'
 for members,pp,flags,want in [
  (13,100,set(),'NO_BILL'),
  (13,49,{'law_passing'},'POOR'),
  (0,100,{'law_passing'},'EMPTY'),
  (13,100,{'law_passing',faction+'_sup'},'ALREADY'),
  (13,50,{'law_passing'},'READY'),
 ]:
  e=env(vars={'lobby_check':choice,faction:members,'supseat_sen':5},pp=pp,flags=flags)
  assert select_func(function,e)=='USA_CONGRESS_LOBBY_'+want,(faction,want)
  assert test(custom['USA_congress_can_lobby'],e)==(want=='READY')
  assert visibility(button+'_supported',e)==(want=='ALREADY')
  assert test(triggers[button+'_click_enabled'],e)==(want=='READY')
  run(effects['lobbying_effect'],e)
  assert e['vars'].get('usa_lobby_result_target',0)==(choice if want=='READY' else 0)
  assert e['pp']==(0 if want=='READY' else pp)
  if want=='READY':
   assert e['vars']['usa_lobby_result_votes']==members
   assert visibility('lobby_feedback',e)
   assert '+13 Senate votes' in expand('[GetUSACongressLobbyFeedback]',e)
   run(effects['clear_support_types'],e)
   assert not visibility('lobby_feedback',e)
for support,pp,flags,want in [(190,100,set(),'NO_BILL'),(190,49,{'law_passing'},'POOR'),(218,100,{'law_passing'},'HOUSE_FULL'),(190,100,{'law_passing'},'READY')]:
 e=env(vars={'lobby_check':10,'supseat':support},pp=pp,flags=flags)
 assert select_func('GetUSACongressLobbyHouseStatus',e)=='USA_CONGRESS_LOBBY_'+want
 run(effects['lobbying_effect'],e)
 assert e['vars']['supseat']==support+(22 if want=='READY' else 0)
 assert e['pp']==pp-(50 if want=='READY' else 0)
 if want=='READY':
  assert e['vars']['usa_lobby_result_votes']==22 and e['vars']['usa_lobby_result_target']==10
  assert '+22 House votes' in expand('[GetUSACongressLobbyFeedback]',e)
  run(effects['lobbying_effect'],e)
  assert e['vars']['supseat']==234 and e['pp']==0
  run(effects['lobbying_effect'],e)
  assert e['vars']['supseat']==234 and e['pp']==0
print('PASS: lobbying tooltips match affordability, eligibility and existing support; success feedback and bill cleanup match actual purchases.')

# Validate every bill's new hooks against its existing success conditions.
assert instrument(bill_source,vote_bills)==bill_source
generated_effects,generated_script,generated_loc=generate_votes(vote_bills)
assert read(vote_effect_file)==generated_effects
assert 'USA_set_congress_vote_requirements = { BILL = $BILL$' not in generated_effects, 'Avoid nested parameter forwarding rejected by the game parser'
assert read(vote_loc_file)==generated_script
assert read('localisation/english/US_Congress_Votes_l_english.yml')==generated_loc
assert '### days_decision_timeout' in (G/'documentation/dynamic_variables_documentation.md').read_text()
assert loc['USA_CONGRESS_VOTE_COUNTDOWN'].count('days_decision_timeout@var:usa_current_legislation')==1
on_actions=read('common/on_actions/USA_congress_gui_on_actions.txt')
assert 'days_decision_timeout' not in on_actions and 'usa_vote_days' not in generated_effects
assert 'set_country_flag' not in generated_effects and 'country_event' not in generated_effects
decision_nodes=get(trees['common/decisions/US_HOUSE.txt'],'CONGRESS_US')
for bill in vote_bills:
 node=get(decision_nodes,bill['key'])
 complete=get(node,'complete_effect');remove=get(node,'remove_effect')
 start=get(complete[-1][2],'USA_begin_congress_vote')
 record=get(remove[0][2],'USA_record_congress_vote')
 assert start and record and start==record,('Vote hook placement',bill['key'])
 assert int(get(start,'HOUSE'))==bill['house'] and get(start,'SENATE')==bill['senate']
 senate=48 if bill['dynamic'] else int(bill['senate'])+1
 for house_votes,senate_votes,passed in [(bill['house'],senate,True),(bill['house']-1,senate,False),(bill['house'],senate-1,False)]:
  e=env(vars={'usa_current_legislation':bill['key'],'senate_passing_value':47,'supseat':house_votes,'supseat_sen':senate_votes,'US_HOUSE_SIZE':435,'US_SENATE':96},flags={'law_passing'})
  run([('USA_begin_congress_vote','=',start)],e)
  assert e['vars']['usa_vote_house_required']==bill['house'] and e['vars']['usa_vote_senate_required']==senate
  assert e['vars']['usa_vote_house_needed']==max(0,bill['house']-house_votes)
  assert e['vars']['usa_vote_senate_needed']==max(0,senate-senate_votes)
  e['decision_timers']={bill['key']:23}
  assert expand('[GetUSACongressVoteCountdown]',e)=='Vote in 23 days'
  e['decision_timers'][bill['key']]=7
  assert expand('[GetUSACongressVoteCountdown]',e)=='Vote in 7 days'
  run([('USA_record_congress_vote','=',record)],e)
  assert e['vars']['usa_last_bill_result']==(1 if passed else 2)
  assert e['vars']['usa_last_house_support']==house_votes and e['vars']['usa_last_senate_support']==senate_votes
  assert e['vars']['usa_last_bill']==bill['key'] and e['vars']['usa_last_bill_short']==bill['short_key']
  run(effects['clear_support_types'],e)
  assert 'usa_vote_house_required' not in e['vars'] and 'usa_current_legislation_short' not in e['vars']
  assert e['vars']['usa_last_bill']==bill['key'] and e['vars']['usa_last_house_support']==house_votes
 short=loc[bill['short_key']]
 assert len(wrapped('hoi_16mbs',short,280))*font_data('hoi_16mbs')[1]<=40,('Last bill name overflow',bill['key'])
for bill in (vote_bills[0],vote_bills[len(vote_bills)//2],vote_bills[-1]):
 e=env(vars={'usa_current_legislation':bill['key'],'senate_passing_value':47},flags={'law_passing'})
 run(effects['USA_recover_congress_vote_metadata'],e)
 assert e['vars']['usa_vote_house_required']==bill['house'] and e['vars']['usa_current_legislation_short']==bill['short_key']
for required,support,enabled in [(217,217,False),(218,217,True),(292,220,True),(292,292,False)]:
 e=env(vars={'lobby_check':10,'usa_vote_house_required':required,'supseat':support},flags={'law_passing'})
 assert test(custom['USA_congress_can_lobby'],e)==enabled
 assert test(triggers['house_lobbying_click_enabled'],e)==enabled
 assert visibility('house_lobbying_supported',e)==(not enabled)
legend=by_name['congress_legend_panel'];assert rect(legend,load_sprite(get(legend,'spriteType')))==(710,223,94,120)
for name,node in by_name.items():
 if name.startswith('congress_legend_'):assert get(node,'pdx_tooltip') is None and get(node,'pdx_tooltip_delayed') is None
for state in STATES:
 suffix={'CT':'Conneticut','DC':'DC','PR':'PR'}.get(state['abbr'],state['name'].replace(' ','_'))
 mask=load_sprite('GFX_NEUTRAL_'+suffix)
 assert mask.getchannel('A').crop((710,223,804,343)).getbbox() is None,('Legend covers a state',state['name'])
for name,node in by_name.items():
 if not name.endswith('_poli_details'):continue
 image=load_sprite(get(node,'spriteType'));x,y,w,h=rect(node,image)
 assert image.getchannel('A').crop((int(710-x),int(223-y),int(804-x),int(343-y))).getbbox() is None,('Legend covers an interactive state mask',name)
assert 'if available' not in LOBBY_LOC.read_text(encoding='utf-8-sig').lower()
assert 'Checked: supporting' not in LOBBY_LOC.read_text(encoding='utf-8-sig')
print('PASS: 517 real vote thresholds, native countdown reads, pass/fail snapshots, saved-vote recovery and offshore legend clearance.')
