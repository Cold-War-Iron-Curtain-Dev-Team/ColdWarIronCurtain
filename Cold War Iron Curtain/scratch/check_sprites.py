import os, re

base = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\interface"
for f in ["IC_goals.gfx", "CWIC_goals.gfx"]:
    path = os.path.join(base, f)
    with open(path, "r", encoding="utf-8", errors="ignore") as fp:
        text = fp.read()
    # find spriteType blocks
    blocks = re.findall(r'SpriteType\s*=\s*\{([^}]+)\}', text)
    for b in blocks:
        if "goals/MLA" in b or "goals/mla" in b:
            m_name = re.search(r'name\s*=\s*"([^"]+)"', b)
            m_tex = re.search(r'texturefile\s*=\s*"([^"]+)"', b)
            name = m_name.group(1) if m_name else "NO_NAME"
            tex = m_tex.group(1) if m_tex else "NO_TEX"
            print(f"{f}: {name} -> {tex}")
