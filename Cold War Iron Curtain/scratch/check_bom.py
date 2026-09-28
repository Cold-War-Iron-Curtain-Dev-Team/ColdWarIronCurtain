import os

p = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\localisation\english\extracted_USA_l_english.yml"
with open(p, "rb") as f:
    header = f.read(3)
    print("Has BOM:", header == b"\xef\xbb\xbf")
