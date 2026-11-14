import re, sys, json
def strip_comments(t):
    return re.sub(r'#[^\n]*', '', t)
def blocks(text):
    """yield (name, body, start, end) for top-level 'name = { ... }'"""
    i=0; n=len(text)
    pat=re.compile(r'([A-Za-z0-9_\.\-:@]+)\s*=\s*\{')
    while True:
        m=pat.search(text,i)
        if not m: return
        d=1; j=m.end()
        while j<n and d:
            c=text[j]
            if c=='{': d+=1
            elif c=='}': d-=1
            j+=1
        yield m.group(1), text[m.end():j-1], m.start(), j
        i=j
def parse(path):
    raw=open(path,encoding='utf-8-sig',errors='replace').read()
    t=strip_comments(raw)
    out=[]
    for name,body,_,_ in blocks(t):
        if name=='ideas':
            for cat,cb,_,_ in blocks(body):
                for idea,ib,_,_ in blocks(cb):
                    out.append((idea,cat,ib))
        else:
            out.append((name,'TOPLEVEL_BROKEN',body))
    return out
if __name__=='__main__':
    for p in sys.argv[1:]:
        for idea,cat,ib in parse(p):
            print(p.split('/')[-1],cat,idea,sep='\t')
