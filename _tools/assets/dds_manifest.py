"""Build a DX9-safe DDS compression manifest for the mod (read-only; writes only the CSV).

Usage (from anywhere):  python _tools/assets/dds_manifest.py [out.csv]

HOI4 ships DX9, DX11, OpenGL and Vulkan renderers, so only formats every one of them can
sample are allowed: BC1 (DXT1) and BC3 (DXT5). BC7 needs DX11 and is not available on
macOS OpenGL; BC5 (ATI2) is a two-channel normal-map format, not a colour format.

Actions per row:
  encode-BC1     raw RGB/RGBA (or DX10 BGRA8) with no alpha in use     -> texconv BC1
  encode-BC3     raw with alpha in use, or a model normal/specular map  -> texconv BC3
  transcode-BC1  DXT3/DXT5 whose alpha is fully opaque                  -> lossless block copy to BC1
  bc7-to-BC3     BC7 file (DX11-only)                                    -> texconv BC3 for DX9/macOS
  skip           fonts, map, flags, particles, cubemaps, odd pixel formats, tiny or unreadable
Non-multiple-of-4 sizes are fine: the mod already ships ~7,000 DXT files like that and vanilla
ships DXT5 portraits at 156x210.

Tier A = models / leaders / event pictures / loading screens (artifacts barely visible)
Tier B = UI (interface, GUI, scripted GUIs, super events) - review before converting
"""
import csv, os, struct, sys
from pathlib import Path
from PIL import Image

MOD = Path(__file__).resolve().parents[2] / 'Cold War Iron Curtain'
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('dds_manifest.csv')

TIER_A = ('gfx/models/', 'gfx/leaders/', 'gfx/event_pictures/', 'gfx/loadingscreens/', 'gfx/entities/')
SKIP_PREFIX = ('gfx/fonts/', 'map/', 'gfx/flags/', 'gfx/particles/', 'gfx/fx/', 'gfx/minimap/')
MATERIAL_HINTS = ('normal', 'spec', '_n.', '_s.', 'nrm', 'properties')
DXGI_RAW32 = {28, 29, 87, 88, 91}  # RGBA8 / BGRA8 (+ sRGB / X variants)
DXGI_BC7 = {98, 99}


def header(data):
    if len(data) < 128 or data[:4] != b'DDS ':
        return None
    height, width = struct.unpack('<II', data[12:20])
    mips = max(1, struct.unpack('<I', data[28:32])[0])
    pf_flags, = struct.unpack('<I', data[80:84])
    fourcc = data[84:88]
    bits, = struct.unpack('<I', data[88:92])
    caps2, = struct.unpack('<I', data[112:116])
    kind, offset = None, 128
    if pf_flags & 4:
        if fourcc == b'DX10' and len(data) >= 148:
            dxgi, = struct.unpack('<I', data[128:132]); offset = 148
            kind = 'raw32' if dxgi in DXGI_RAW32 else 'bc7' if dxgi in DXGI_BC7 else f'dxgi{dxgi}'
        else:
            kind = fourcc.decode('latin1')
    else:
        kind = f'raw{bits}'
    return dict(w=width, h=height, mips=mips, kind=kind, offset=offset,
                cube=bool(caps2 & 0x200) or bool(caps2 & 0x200000))


def blocks_bytes(w, h, mips, bytes_per_block):
    return sum(((max(1, w >> i) + 3) // 4) * ((max(1, h >> i) + 3) // 4) for i in range(mips)) * bytes_per_block


def dxt5_block_opaque(b):
    a0, a1 = b[0], b[1]
    if a0 == 255 and a1 == 255:
        return True
    bits = int.from_bytes(b[2:8], 'little')
    if a0 > a1:
        pal = [a0, a1] + [((7 - i) * a0 + i * a1) // 7 for i in range(1, 7)]
    else:
        pal = [a0, a1] + [((5 - i) * a0 + i * a1) // 5 for i in range(1, 5)] + [0, 255]
    return all(pal[(bits >> (3 * i)) & 7] == 255 for i in range(16))


def dxt_opaque(data, kind, offset):
    body = data[offset:offset + (len(data) - offset) // 16 * 16]
    n = len(body) // 16
    if kind == 'DXT3':
        return all(body[j::16].count(255) == n for j in range(8))
    if body[0::16].count(255) == n and body[1::16].count(255) == n:
        return True
    return all(dxt5_block_opaque(body[16 * i:16 * i + 8]) for i in range(n))


def alpha_used(path):
    im = Image.open(path)
    im.load()
    if im.mode not in ('RGBA', 'LA', 'PA'):
        return False
    return im.getchannel('A').getextrema()[0] < 255


def classify(path, rel, data, hd):
    lo = rel.lower()
    name = lo.rsplit('/', 1)[-1]
    material = lo.startswith('gfx/models/') and any(h in name for h in MATERIAL_HINTS)
    w, h, mips, kind = hd['w'], hd['h'], hd['mips'], hd['kind']
    if lo.startswith(SKIP_PREFIX):
        return 'skip', 'excluded folder', ''
    if hd['cube']:
        return 'skip', 'cubemap/volume', ''
    if kind in ('DXT3', 'DXT5'):
        if material:
            return 'skip', 'model material map (keep alpha)', ''
        if dxt_opaque(data, kind, hd['offset']):
            return 'transcode-BC1', '', 'no'
        return 'skip', 'already DXT with alpha', 'yes'
    if kind in ('DXT1', 'ATI2', 'ATI1', 'BC4U', 'BC5U'):
        return 'skip', 'already compressed', ''
    if kind == 'bc7':
        return 'bc7-to-BC3', '', ''
    if kind not in ('raw24', 'raw32', 'raw32'):
        return 'skip', f'{kind} format', ''
    if w * h < 32 * 32:
        return 'skip', 'tiny (<32x32)', ''
    try:
        used = alpha_used(path)
    except Exception as e:  # unreadable by Pillow -> leave alone
        return 'skip', f'unreadable: {type(e).__name__}', ''
    return ('encode-BC3' if (used or material) else 'encode-BC1'), '', 'yes' if used else 'no'


def main():
    rows = []
    for dp, dn, fn in os.walk(MOD):
        for f in fn:
            if not f.lower().endswith('.dds'):
                continue
            p = Path(dp) / f
            rel = p.relative_to(MOD).as_posix()
            data = p.read_bytes()
            hd = header(data)
            if not hd:
                continue
            action, reason, alpha = classify(p, rel, data, hd)
            est = len(data)
            if action != 'skip':
                bpb = 8 if action.endswith('BC1') else 16
                est = 128 + blocks_bytes(hd['w'], hd['h'], hd['mips'], bpb)
            rows.append(dict(path=rel, source=hd['kind'], width=hd['w'], height=hd['h'], mips=hd['mips'],
                             tier='A' if rel.lower().startswith(TIER_A) else 'B', alpha=alpha,
                             action=action, size=len(data), est_size=est, reason=reason))
    rows.sort(key=lambda r: -(r['size'] - r['est_size']))
    with open(OUT, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    MB = 1048576
    groups = {}
    for r in rows:
        if r['action'] == 'skip':
            continue
        g = groups.setdefault((r['action'], r['tier']), [0, 0, 0])
        g[0] += 1; g[1] += r['size']; g[2] += r['est_size']
    total = 0
    for (action, tier), (n, cur, new) in sorted(groups.items()):
        total += cur - new
        print(f'{action:14s} tier {tier}: {n:6d} files  {cur / MB:7.0f} MB -> {new / MB:6.0f} MB  saves {(cur - new) / MB:6.0f} MB')
    print(f'TOTAL estimated saving: {total / MB:.0f} MB')
    skips = {}
    for r in rows:
        if r['action'] == 'skip':
            k = r['reason'].split(':')[0]
            skips.setdefault(k, [0, 0]); skips[k][0] += 1; skips[k][1] += r['size']
    for k, (n, s) in sorted(skips.items(), key=lambda x: -x[1][1]):
        print(f'  skip {k}: {n} files, {s / MB:.0f} MB')
    print('manifest:', OUT)


if __name__ == '__main__':
    main()
