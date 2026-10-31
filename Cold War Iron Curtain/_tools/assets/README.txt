Mod package size cleanup

From the repository root:
  python "Cold War Iron Curtain/_tools/assets/reduce_package_size.py"
  python "Cold War Iron Curtain/_tools/assets/reduce_package_size.py" --apply
  python "Cold War Iron Curtain/_tools/assets/reduce_package_size.py" --check

The default is a dry run. Applying requires Pillow for independent DDS decoding.

Japanese fonts: only single-page DXT5 atlases with one texture level are trimmed.
The tool keeps the full width, every glyph rectangle and four pixels below the
lowest glyph, rounding the height up to a multiple of four. It copies the existing
compressed blocks without decoding/re-encoding them, updates the DDS height and
linear size, and changes only scaleH in the corresponding FNT. Existing sibling
atlas naming is retained. Multi-page fonts and other formats are left intact.
Before applying, Pillow verifies that every retained pixel in all RGBA channels
is identical. Font layout, character counts, offsets, advances and kerning stay
unchanged. An in-game Japanese UI check is still appropriate after restarting.

Editable art: PSD and Paint.NET PDN files are moved, preserving their relative
paths, to:
  CWIC Backup/Source Art Moved From Active Mod/Cold War Iron Curtain/
This location is outside the active mod directory. It retains the source art;
the rendered DDS/PNG/etc. assets used by the game are not moved. Disabled scripts
are outside this tool's scope. The map planning layer is now archived at:
  CWIC Backup/Source Art Moved From Active Mod/Cold War Iron Curtain/map/provinces.pdn

Hashes, original/new atlas dimensions and all source-art destinations are recorded
in CWIC Backup/Source Art Moved From Active Mod/asset_cleanup_manifest.json.
--check verifies this manifest, atlas dimensions and every glyph's bounds.
The tool stages font changes and verifies hashes before replacing files, with
temporary rollback copies under _local/mod-package-reduction. Those temporary
copies are removed after successful verification. Re-running is a no-op once
the files have been compacted. It never commits or rewrites Git history.

Format references:
  https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dds-header
  https://www.angelcode.com/products/bmfont/doc/file_format.html
