"""Apply a dds_manifest.csv: compress DDS textures to DX9-safe BC1/BC3.

Usage (from anywhere):
  python _tools/assets/dds_compress.py MANIFEST [--texconv PATH] [--tier A|B|all]
         [--actions transcode-BC1,encode-BC1,encode-BC3,bc7-to-BC3] [--prefix gfx/models/]
         [--limit N] [--min-psnr 30] [--apply] [--log out.csv]

Without --apply nothing in the mod is written: every file is converted into a temp folder,
checked, and reported. With --apply each verified result replaces the original in place
(use git to roll back).

transcode-BC1  lossless: copies the colour blocks of an opaque DXT3/DXT5 into BC1 and checks
               the decoded pixels are identical.
encode-*       runs Microsoft texconv (-dx9 legacy header, same mip count, sRGB kept as-is)
               and rejects any result whose top-mip PSNR is below --min-psnr.
"""
import argparse, csv, io, math, os, shutil, struct, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

MOD = Path(__file__).resolve().parents[2] / 'Cold War Iron Curtain'
SRGB_DXGI = {29, 72, 78, 91, 93, 99}


# ---------------- lossless DXT3/DXT5 -> BC1 ----------------
def _bc1_block_from_colour(c):
    """c = 8-byte colour block from a DXT3/DXT5 (always decoded in 4-colour mode)."""
    c0, c1 = struct.unpack('<HH', c[:4]); idx = int.from_bytes(c[4:8], 'little')
    if c0 > c1:
        return bytes(c)
    if c0 == c1:  # every palette entry equals c0; BC1 3-colour mode would make index 3 transparent
        return c[:4] + b'\x00\x00\x00\x00'
    # c0 < c1: swap endpoints so BC1 stays in 4-colour mode, remap indices 0<->1, 2<->3
    out = 0
    for i in range(16):
        out |= (((idx >> (2 * i)) & 3) ^ 1) << (2 * i)
    return struct.pack('<HH', c1, c0) + out.to_bytes(4, 'little')


def transcode_to_bc1(data):
    if data[84:88] not in (b'DXT3', b'DXT5'):
        raise ValueError('not DXT3/DXT5')
    body = data[128:]
    n = len(body) // 16
    out = bytearray()
    for i in range(n):
        out += _bc1_block_from_colour(body[16 * i + 8:16 * i + 16])
    hdr = bytearray(data[:128])
    w, = struct.unpack('<I', hdr[16:20]); h, = struct.unpack('<I', hdr[12:16])
    hdr[84:88] = b'DXT1'
    hdr[20:24] = struct.pack('<I', max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * 8)  # linear size
    return bytes(hdr) + bytes(out)


# ---------------- verification ----------------
def decode(data):
    im = Image.open(io.BytesIO(data)); im.load()
    return im.convert('RGBA')


def psnr(a, b, alpha=True):
    if a.size != b.size:
        return -1.0
    bands = ('R', 'G', 'B', 'A') if alpha else ('R', 'G', 'B')
    se = n = 0
    for band in bands:
        ha = a.getchannel(band).tobytes(); hb = b.getchannel(band).tobytes()
        se += sum((x - y) ** 2 for x, y in zip(ha, hb)); n += len(ha)
    mse = se / max(n, 1)
    return 99.0 if mse == 0 else 10 * math.log10(255 * 255 / mse)


# ---------------- texconv ----------------
def texconv_encode(texconv, src, fmt, mips, srgb, tmpdir):
    f = f'{fmt}_UNORM_SRGB' if srgb else f'{fmt}_UNORM'
    cmd = [texconv, '-nologo', '-y', '-dx9', '-f', f, '-m', str(mips), '-o', str(tmpdir), str(src)]
    if srgb:
        cmd[3:3] = ['-srgb']  # keep the data in its own colour space: no linear/sRGB conversion
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = Path(tmpdir) / (src.stem + '.dds')
    if r.returncode != 0 or not out.exists():
        raise RuntimeError((r.stdout + r.stderr).strip()[-300:])
    return out.read_bytes()


def source_is_srgb(data):
    return data[84:88] == b'DX10' and struct.unpack('<I', data[128:132])[0] in SRGB_DXGI


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('manifest')
    ap.add_argument('--texconv')
    ap.add_argument('--tier', default='all')
    ap.add_argument('--actions', default='transcode-BC1,encode-BC1,encode-BC3,bc7-to-BC3')
    ap.add_argument('--prefix', default='')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--min-psnr', type=float, default=30.0)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--log', default='')
    a = ap.parse_args()
    actions = set(a.actions.split(','))
    rows = [r for r in csv.DictReader(open(a.manifest, encoding='utf-8'))
            if r['action'] in actions and (a.tier == 'all' or r['tier'] == a.tier)
            and r['path'].lower().startswith(a.prefix.lower())]
    if a.limit:
        rows = rows[:a.limit]
    if any(r['action'] != 'transcode-BC1' for r in rows) and not a.texconv:
        sys.exit('texconv is required for encode-* / bc7-to-BC3 rows (pass --texconv PATH)')
    log = []; before = after = 0; MB = 1048576
    with tempfile.TemporaryDirectory(prefix='cwic-dds-') as tmp:
        for i, r in enumerate(rows, 1):
            p = MOD / r['path']; data = p.read_bytes(); status = 'ok'; q = ''
            try:
                if r['action'] == 'transcode-BC1':
                    new = transcode_to_bc1(data)
                    ref = decode(data); got = decode(new)
                    if ref.convert('RGB').tobytes() != got.convert('RGB').tobytes():
                        raise RuntimeError('transcode not pixel-identical')
                    q = 'lossless'
                else:
                    fmt = 'BC1' if r['action'] == 'encode-BC1' else 'BC3'
                    new = texconv_encode(a.texconv, p, fmt, int(r['mips']), source_is_srgb(data), tmp)
                    s = psnr(decode(data), decode(new), alpha=(fmt == 'BC3'))
                    q = f'{s:.1f}'
                    if s < a.min_psnr:
                        raise RuntimeError(f'PSNR {s:.1f} dB below {a.min_psnr}')
                if len(new) >= len(data):
                    raise RuntimeError('not smaller')
                if a.apply:
                    p.write_bytes(new)
                before += len(data); after += len(new)
            except Exception as e:
                status = f'rejected: {e}'
            log.append(dict(path=r['path'], action=r['action'], tier=r['tier'], old=len(data),
                            new=len(new) if status == 'ok' else len(data), quality=q, status=status))
            if i % 500 == 0:
                print(f'  {i}/{len(rows)} ...', flush=True)
    ok = sum(l['status'] == 'ok' for l in log)
    print(f"{'APPLIED' if a.apply else 'DRY RUN'}: {ok}/{len(log)} converted, "
          f"{before / MB:.1f} MB -> {after / MB:.1f} MB (saves {(before - after) / MB:.1f} MB); "
          f"{len(log) - ok} rejected")
    if a.log and log:
        with open(a.log, 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=list(log[0].keys())); w.writeheader(); w.writerows(log)
        print('log:', a.log)


if __name__ == '__main__':
    main()
