p = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\localisation\english\extracted_USA_l_english.yml"
with open(p, "rb") as f:
    content = f.read()

if not content.startswith(b"\xef\xbb\xbf"):
    with open(p, "wb") as f:
        f.write(b"\xef\xbb\xbf" + content)
    print("Added UTF-8 BOM successfully.")
else:
    print("BOM already present.")
