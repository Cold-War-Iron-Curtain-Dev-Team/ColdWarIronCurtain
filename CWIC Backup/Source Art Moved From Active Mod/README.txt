Preserved editable source art

Cold War Iron Curtain/ mirrors paths inside the active mod directory. These are
editable originals, stored here so PSD/PDN files do not inflate the game package.
Rendered runtime images remain in the active mod. Open or copy an archived file
when editing its source, then export the finished texture to the active mod.

The newer PSD/PDN moves and Japanese font atlas reductions are recorded with
SHA-256 hashes in asset_cleanup_manifest.json. Earlier archived source files
predate that manifest. The Soviet map planning layer is available at:
  Cold War Iron Curtain/map/provinces.pdn

Verification and cleanup tool:
  python "Cold War Iron Curtain/_tools/assets/reduce_package_size.py" --check

Moving source art here reduces the active mod/package size, while keeping its
original bytes on this drive. Cropping unused font atlas rows also frees disk
space. Git history is not changed by this tool.
