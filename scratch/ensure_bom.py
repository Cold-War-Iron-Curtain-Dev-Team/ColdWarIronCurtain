p = 'Cold War Iron Curtain/localisation/english/extracted_USA_l_english.yml'
with open(p, 'rb') as f:
    raw = f.read()

if raw.startswith(b'\xef\xbb\xbf'):
    print("BOM already present!")
else:
    print("Adding BOM...")
    with open(p, 'wb') as f:
        f.write(b'\xef\xbb\xbf' + raw)
    print("BOM added successfully!")

with open(p, 'rb') as f:
    check = f.read(3)
    assert check == b'\xef\xbb\xbf', "Failed to verify BOM!"
    print("Verified UTF-8 BOM present!")
