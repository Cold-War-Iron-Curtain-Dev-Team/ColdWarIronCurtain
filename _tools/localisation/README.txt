Audited vanilla English localisation recovery

From the repository root:
  python "Cold War Iron Curtain/_tools/localisation/restore_vanilla.py" --check
  python "Cold War Iron Curtain/_tools/localisation/restore_vanilla.py" --write
Add --game-dir "path/to/Hearts of Iron IV" for a different vanilla installation.

Inputs:
  recovery_keys.txt: the 1,155 keys selected by the vanilla recovery audit
    (503 priority + 652 additional candidates).
  cwic_aliases.json: 45 aliases to existing CWIC text. These preserve CWIC's
    reused country tags and route old bookmark key names to the existing 1949
    histories. Brazil has no corresponding 1949 history, so its missing
    bookmark fallback uses the existing CWIC world introduction.

Outputs:
  localisation/english/CWIC_vanilla_recovery_l_english.yml
  common/scripted_localisation/CWIC_vanilla_loc_recovery.txt
  _tools/localisation/recovery_manifest.json

The generator restores only selected keys that are absent from all other mod
English files and unshadowed vanilla files. It copies their installed vanilla
values and follows hidden $KEY$ dependencies. It preserves existing CWIC text,
rejects ambiguous vanilla definitions, checks alias closure and rejects new
alias cycles. The English output uses UTF-8 BOM and contains no duplicate keys.

Two vanilla defined_text functions are required by the restored legacy SS-event
text: GetSSAngerLevel and GetWehrmachtAngerLevel. Only those localisation blocks
and their six missing text labels are restored; no events, decisions, effects,
focuses or other vanilla gameplay content is activated by this generator.

The initial recovery contains 1,162 entries: all 1,155 audited keys plus seven
dependencies (six SS anger labels and the nuclear submarine hull description).
The manifest records the source file and line for each entry, all dependency
additions and every CWIC-specific alias. The audit was static; an in-game reload
and loc_check are still useful for dynamic localisation beyond this fixed list.

If an audited key is later defined elsewhere in CWIC, rebuilding omits it here
to preserve that definition and avoid duplicate keys. The key list is fixed;
this tool does not indiscriminately import suppressed vanilla localisation.
