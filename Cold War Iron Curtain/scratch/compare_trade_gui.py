vanilla_path = r"G:\steamlbirary\steamapps\common\Hearts of Iron IV\interface\countrytradeview.gui"
mod_path = r"interface\countrytradeview.gui"

with open(vanilla_path, 'r', encoding='utf-8', errors='ignore') as f:
    v = f.read()

with open(mod_path, 'r', encoding='utf-8', errors='ignore') as f:
    m = f.read()

def get_block(text, name):
    idx = text.find(name)
    if idx == -1: return 'NOT FOUND'
    return text[idx:idx+1500]

print('=== VANILLA resources_info_entry ===')
print(get_block(v, 'name = "resources_info_entry"'))

print('\n=== MOD resources_info_entry ===')
print(get_block(m, 'name = "resources_info_entry"'))
