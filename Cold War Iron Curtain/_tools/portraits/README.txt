CWIC random military portraits

Run from the mod directory:
  python _tools/portraits/repair_portraits.py --game-dir "D:/SteamLibrary/steamapps/common/Hearts of Iron IV"
  python _tools/portraits/repair_portraits.py --game-dir "D:/SteamLibrary/steamapps/common/Hearts of Iron IV" --check

Rebuilding requires Pillow; --check uses only the Python standard library.

The game uses portraits/00_portraits.txt for random generals, division officers,
admirals and ship captains. The generator imports vanilla military pools and
uses their existing large/small sprite pairs. It does not copy vanilla art or
introduce another in-game portrait-selection system.

We must retain a replacement 00_portraits.txt rather than simply remove ours:
  - Vanilla SAR/SMI/TML are Sarawak/Sami/Timor-Leste; in CWIC they are
    Saarland/the Imamate of Oman/Tamil.
  - Current vanilla pools include optional DLC-only sprites, including entire
    Indian naval pools. Pool membership must be identical in mixed-DLC games.
  - CWIC has political ideologies and political placeholder pools to preserve.

Only base-game pairs are imported. Indian naval pools use the older base-game
Indian admirals. The existing
four DLC portrait-pool suppression files remain in place. On a HOI4 update,
regenerate and review the diff; --check detects drift against the installed game.

SUPPLEMENTS in the generator records CWIC country/region exceptions. Everything
else uses vanilla national pools where present, or the seven continental pools.
Do not automatically map religious graphical cultures to faces: several CWIC
countries use those settings for religion or colonial administration.

South Korea retains its 29 custom army portraits. The generator compiles their
65x67 small portraits from the existing artwork. The neutral military silhouette
also gets a small portrait, because CWIC's idea_unknown.dds is a debug banner.
The political Giga_Panther placeholder retains its appearance and now has a
proper sprite pair. Required generic sprite definitions hidden by CWIC's
_leader_portraits.gfx override are restored without importing WW2 characters.

Validation checks balanced output, repeatable generation, national army/navy
coverage, every large/small sprite and texture against a DLC-free installation,
thumbnail dimensions, US/Saarland regression cases, and DLC pool suppression.

In-game smoke check after restarting HOI4 (prefer a new campaign):
  - USA: inspect new division officers and ship captains, recruit a general and
    admiral, then promote an officer/captain and compare both portrait sizes.
  - Repeat for WGR/DDR, RUS, KOR, RAJ, INO, SAR, MOR and an African minor.
  - Check a mixed-DLC multiplayer lobby for identical pool behavior.

Portraits already stored in a save are not retroactively reassigned by this
repair. No save migration is included. The military-pool generator does not
alter named officers; related definition repairs are described below.

Related identity repairs

  python _tools/portraits/repair_identity.py --game-dir "D:/SteamLibrary/steamapps/common/Hearts of Iron IV"
  python _tools/portraits/repair_identity.py --game-dir "D:/SteamLibrary/steamapps/common/Hearts of Iron IV" --check

This second generator adds the missing name lists, removes hard-coded German
names from temporary D01-D75 tags, and corrects the US lists copied into Twipra
and Manipur. It reuses CWIC/vanilla personal names without copying operation
names. NAME_SOURCES records each choice. Small regional minorities and Pacific
islands use the closest existing regional lists where no dedicated list exists;
these are fallbacks, not a claim of historically complete name coverage.

Operatives use native portrait pools in 10_cwic_operative_portraits.txt. Both
genders have continental coverage, with country exceptions for South Asia,
Central Asia, Eastern Europe and countries spanning continental boundaries.
Explicitly labelled generic CWIC operative artwork is used for men where
available; existing base-game generic civilian faces supply the other slots.
The unclassified novelty/costume pictures are not added to the random pools.
Operative portraits use the same large-only sprite convention as native LaR
operative pools. The DLC pool-suppression files remain unchanged.

The generator also builds paired portraits for Qassem Munaser and Mohamed bin
Hussein. Their named-character and legacy CSA definitions now agree on identity.
Other named-character repairs are direct path/sprite fixes in their source files,
including restoration of the vanilla large/small pair for Marijan Polic.

The --check command validates name coverage for every permanent country, both
genders in every operative pool, both Yemeni thumbnails and all nonempty portrait
references in every named-character file against a DLC-free virtual filesystem.
In-game checks: recruit male/female operatives in SYR/VTC/RAJ/INO; inspect new
names in DAG/KIR/CLL; start a non-German civil war and check generated names;
inspect the repaired historical officers at both portrait sizes.
