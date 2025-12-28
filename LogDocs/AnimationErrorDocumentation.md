# Animation and Entity Error Documentation - Generated with AI

## Overview
This document details all remaining errors, code changes made, and items that need to be created or edited regarding animations and entities.

---

## 1. FIXED ERRORS

### 1.1 Missing Mesh Files (Fixed with Placeholders)
The following missing mesh files were replaced with compatible placeholders:

#### Infantry/Paratrooper/Marine Meshes
- `YUG_paratrooper_1.mesh` → `YUG_infantry_1.mesh` (used in `ARG_marine_3_mesh`, `ARG_marine_4_mesh`)
- `LAO_militia_0.mesh` → `LAO_infantry_0.mesh` or `LAO_infantry_1.mesh` (used in `LOS_militia_X_mesh`)
- `LAO_militia_1.mesh` → `LAO_infantry_1.mesh` (used in `LOS_militia_1_mesh`)
- `PRC_paratrooper_1.mesh` → `PRC_infantry_1.mesh` (used in `LEB_infantry_2_mesh`)
- `CZE_paratrooper.mesh` → `CZE_paratrooper_0.mesh` (used in `CUB_marine_1_mesh`, `CUB_marine_2_mesh`, `LEB_marine_mesh`)
- `USA_mountaineer.mesh` → `USA_mountaineer_0.mesh` (used in `ARG_marine_1_mesh`, `ARG_marine_2_mesh`)
- `ENG_infantry_2.mesh` → `NEW_NATO_models/ENG_infantry_2.mesh` (used in `IRE_infantry_2_mesh`, `IRE_infantry_4_mesh`)
- `TUR_infantry_1.mesh` → `NEW_NATO_models/TUR_infantry_1.mesh` (used in `CHL_infantry_2_mesh`)
- `DDR_mountaineers_2.mesh` → `DDR_paratrooper_0.mesh` (used in `CHL_infantry_3_mesh`)
- `ENG_mountaineers.mesh` → `ENG_infantry_0.mesh` (used in `CHL_infantry_4_mesh`, `SAF_infantry_2_mesh`)
- `IC_South_Vietnam.mesh` → `VNA_infantry_1.mesh` (used in `SAF_infantry_3_mesh`, `SAF_marine_2_mesh`, `SAF_marine_4_mesh`)
- `JAP_infantry_1.mesh` → `NEW_NATO_models/JAP_infantry_1.mesh` (used in `JAP_paratrooper_1_mesh`)
- `AFG_infantry_2.mesh` → `AFG_infantry_0.mesh` (used in `ETH_infantry_4_mesh`)
- `CHI_infantry_2.mesh` → `NEW_NATO_models/CHI_infantry_2.mesh` (used in `BRA_infantry_2_mesh`)
- `FRA_infantry_2.mesh` → `NEW_NATO_models/FRA_infantry_2.mesh` (used in `BRA_infantry_3_mesh`)
- `WGR_infantry_2.mesh` → `NEW_NATO_models/WGR_infantry_2.mesh` (used in `AUS_infantry_2_mesh`)
- `PRC_infantry_X_snow.mesh` → `PRC_infantry_snow_X.mesh` (multiple entries)
- `PRC_infantry_X_desert.mesh` → `PRC_infantry_desert_X.mesh` (multiple entries)
- `CUB_infantry_test_X.mesh` → `CUB_infantry_1.mesh` or `CUB_infantry_2.mesh` (multiple entries)
- `KOR_paratrooper_3.mesh` → `KOR_paratrooper_2.mesh` (used in `KOR_paratrooper_3_mesh`)
- `FRA_marine_3.mesh` → `NEW_NATO_models/FRA_marine_3.mesh` (used in `FRA_marine_3_mesh`)
- `FRA_marine_4.mesh` → `NEW_NATO_models/FRA_marine_4.mesh` (used in `FRA_marine_4_mesh`)
- `MAL_infantry_3.mesh` → `NEW_SEA_models/MAL_infantry_3.mesh` (used in `MAL_infantry_3_desert_mesh`, `MAL_infantry_3_snow_mesh`, `MAL_paratrooper_3_mesh`)
- `FRE_paratrooper_4.mesh` → `NEW_NATO_models/FRA_paratrooper_4.mesh` (used in `FRE_paratrooper_3_mesh`)
- `FRE_FFL_0.mesh` → `NEW_NATO_models/FRE_FFL_0.mesh` (used in `FRE_ffl_0_mesh`)
- `MEO_militia_0.mesh` → `NEW_SEA_models/MEO_militia_0.mesh` (used in `MEO_infantry_0_mesh`)

#### Tank Meshes
- `m47.mesh` → `m47a1.mesh` (used in `usa_m47_mesh`, `JOR_m47_mesh`)
- `m60.mesh` → `m60a1.mesh` (used in `CHI_m60_mesh`, `EGY_m60_mesh`, `USA_m60_mesh`, `JOR_m60_mesh`)
- `m60a.mesh` → `m60a1.mesh` (used in `usa_m60a_mesh`)
- `t55.mesh` → `T62.mesh` (used in `sov_t62_mesh`, later corrected to use `m48a1` animations)
- `DDR_mountaineers_2.mesh` → `DDR_paratrooper_0.mesh` (used in `CHL_infantry_3_mesh`)
- `ENG_mountaineers.mesh` → `ENG_infantry_0.mesh` (used in `CHL_infantry_4_mesh`)
- `FRA_tank_AMX.mesh` → `FRA_tank_medium.mesh` (used in `FRA_tank_AMX_mesh`)

#### Vehicle Meshes
- `boxer_ger.mesh` → `gfx/models/units/vehicles/boxer_ger.mesh` (used in `WGR_mechanized_vec3_mesh`)

#### Weapon Meshes
- `AK_Joro.mesh` → `AK47.mesh` (used in `FIN_infantry_weapon_AK_mesh`)

#### Train Meshes
- All missing `train_coal_equipment_X.mesh` files → `SOV_train.mesh` (used in multiple train meshes)

### 1.2 Animation Compatibility Errors (Fixed)
The following animation compatibility issues were resolved by changing animations to match mesh joint counts:

#### Tank Animations
- `sov_t62_mesh`: Changed from `t55_X_animation` (10 joints) to `m48a1_X_animation` (15 joints) to match `T62.mesh` (15 joints)
- `M1A1Abrams_mesh`: Changed from `m48a1_X_animation` (15 joints) to `generic_tank_medium_X_animation` (24 joints) to match `M1A1Abrams.mesh` (24 joints)
- `usa_m47_mesh`: Changed from `generic_tank_medium_X_animation` (24 joints) to `m48a1_X_animation` (15 joints) to match `m47a1.mesh` (15 joints)
- `usa_m60a_mesh`: Changed from `generic_tank_medium_X_animation` (24 joints) to `m60a1_X_animation` (15 joints) to match `m60a1.mesh` (15 joints)
- `m48_mesh`: Changed from `m48_X_animation` (11 joints) to `m48a1_X_animation` (15 joints) to match `m48.mesh` (15 joints)
- `m60_mesh`: Changed from `m60_X_animation` (11 joints) to `m60a1_X_animation` (15 joints) to match `m60a1.mesh` (15 joints)
- `CHI_m48_mesh`: Changed to `m48a1_X_animation`
- `CHI_m60_mesh`: Changed from `m60_X_animation` (11 joints) to `m60a1_X_animation` (15 joints) to match `m60a1.mesh` (15 joints)
- `NOR_m48_mesh`: Changed to `m48a1_X_animation`
- `JOR_m60_mesh`: Changed from `generic_tank_medium_X_animation` (24 joints) to `m60a1_X_animation` (15 joints) to match `m60a1.mesh` (15 joints)
- `JOR_m47_mesh`: Changed from `generic_tank_medium_X_animation` (24 joints) to `m48a1_X_animation` (15 joints) to match `m47a1.mesh` (15 joints)
- `EGY_t55_mesh`: Changed from `t55_X_animation` (10 joints) to `generic_tank_medium_X_animation` (24 joints) to match `t55.mesh` (24 joints)
- `EGY_m60_mesh`: Changed from `m60_X_animation` (11 joints) to `m60a1_X_animation` (15 joints) to match `m60a1.mesh` (15 joints)
- `SYR_t55_mesh`: Changed from `t55_X_animation` (10 joints) to `generic_tank_medium_X_animation` (24 joints) to match `t55.mesh` (24 joints)
- `FIN_T55_mesh`: Changed from `m48a1_X_animation` (15 joints) to `generic_tank_medium_X_animation` (24 joints) to match `T55A.mesh` (24 joints)

#### Vehicle Animations
- `DDR_mtlb_mesh`: Changed from `mtlb_X_animation` (14/1 joints) to `generic_tank_medium_X_animation` (24 joints) to match `mtlb.mesh` (24 joints)

### 1.3 Missing Skeleton Errors (Fixed)
The following meshes have no skeleton, so their animations were commented out:

- `DDR_IS2.mesh` (used in `DDR_IS2_mesh`)
- `Moskva.mesh` (used in `SOV_Moskva_mesh`)
- `SOV_train.mesh` (used in multiple train meshes)
- `SU25UTI.mesh` (used in `su25UTI_mesh`)
- `SOV_Il6.mesh` (used in `SOV_Il6_mesh`)
- `il28.mesh` (used in `il28_mesh`)
- `Be6.mesh` (used in `Be6_mesh`)
- `btrkaz.mesh` (used in `SOV_marine_vec3_mesh`)
- `brdm2_BUL.mesh` (used in `BUL_mechanized_airborne_vec1_mesh`)

### 1.4 New Mesh Definitions Added
The following mesh definitions were added to resolve "Couldn't find mesh" errors:

- `ENG_light_armor_2_mesh` (added to `ENG_tanks.gfx`)
- `MAL_infantry_3_mesh` (added to `MAL_unit.gfx`)
- `KOR_infantryMG_mesh` (added to `KOR_unit.gfx`)
- `KOR_infantryMG_1_mesh` (added to `KOR_unit.gfx`)
- `FRA_infantrymg_2_mesh` (added to `FRA_unit.gfx`)
- `FRE_paratrooper_4_mesh` (added to `FRE_unit.gfx`)
- `WGR_armored_vec3_mesh` (added to `WGR_vehicles.gfx`)
- `MEO_infantry_0_mesh` (added to `ethnostates_unit.gfx`)

---

## 2. REMAINING ERRORS

### 2.1 Duplicate Animation Error
**Error:** `Duplicated animation: "GER_infantry_mg_idle_animation"`

**Status:** UNRESOLVED - Likely a game engine quirk. No duplicate definitions found within the same `pdxmesh` block or across files. This may be a false positive or an internal engine issue.

**Action Required:** None - This appears to be a non-critical warning that doesn't affect functionality.

---

### 2.2 Missing Mesh Definitions (Entity References)
The following meshes are referenced in `.asset` files but are not defined as `pdxmesh` in any `.gfx` file:

#### Tank/Armor Meshes
- `USA_heavy_armor_1_mesh` (referenced by `CAN_heavy_armor_entity`)
- `USA_super_heavy_armor_mesh` (referenced by `CAN_super_heavy_armor_entity`, `CHI_super_heavy_armor_entity`, `ISR_super_heavy_armor_entity`, `JAP_super_heavy_armor_entity`, `JOR_super_heavy_armor_entity`, `KOR_super_heavy_armor_entity`, `USA_super_heavy_armor_entity`)
- `SOV_light_armor_2_mesh` (referenced by `CZE_light_armor_0_entity`, `DDR_light_armor_0_entity`, `HUN_light_armor_0_entity`, `POL_light_armor_0_entity`, `ROM_light_armor_0_entity`, `SOV_light_armor_0_entity`)
- `SOV_heavy_armor_2_mesh` (referenced by `CZE_heavy_armor_0_entity`, `DDR_heavy_armor_0_entity`, `HUN_heavy_armor_0_entity`, `POL_heavy_armor_0_entity`, `ROM_heavy_armor_0_entity`, `SOV_heavy_armor_0_entity`)
- `SOV_super_heavy_armor_mesh` (referenced by `CZE_super_heavy_armor_1_entity`, `DDR_super_heavy_armor_1_entity`, `HUN_super_heavy_armor_1_entity`, `KPA_super_heavy_armor_entity`, `POL_super_heavy_armor_1_entity`, `PRC_super_heavy_armor_entity`, `ROM_super_heavy_armor_1_entity`, `VIN_super_heavy_armor_entity`)
- `USA_advanced_medium_tank_destroyer_mesh` (referenced by `ISR_tank_destroyer_entity`, `JAP_tank_destroyer_entity`, `KOR_tank_destroyer_entity`, `USA_tank_destroyer_entity`)
- `FRA_light_armor_2_mesh` (referenced by `FRA_light_armor_entity`)
- `ENG_light_armor_1_mesh` (referenced by `commonwealth_gfx_light_armor_entity`)
- `ENG_medium_armor_1_mesh` (referenced by `commonwealth_gfx_medium_armor_entity`)
- `ENG_heavy_armor_0_mesh` (referenced by `commonwealth_gfx_heavy_armor_entity`)

#### Infantry Meshes
- `ARG_marine_4_mesh` (referenced by `ARG_mountaineers_0_entity`, `ARG_mountaineers_1_entity`)

**Action Required:** 
1. Create `pdxmesh` definitions for these meshes in appropriate `.gfx` files, or
2. Update the entity definitions in `.asset` files to reference existing meshes

---

### 2.3 Missing Animation IDs in Entity States
The following entities reference animation IDs that are not defined in their associated `pdxmesh` blocks:

#### Missing "charge_rifle" and "charge_rifle_shoot" Animations
These entities reference `charge_rifle` and `charge_rifle_shoot` animations that don't exist in their meshes:
- `AFG_airborne_0_entity`
- `ALG_mountaineers_1_entity`, `ALG_airborne_0_entity`, `ALG_airborne_1_entity`, `ALG_aircav_1_entity`
- `BUL_mountaineers_2_entity`, `BUL_mountaineers_3_entity`
- `CAN_marine_1_entity`, `CAN_mountaineers_1_entity`, `CAN_airborne_0_entity`, `CAN_airborne_1_entity`, `CAN_aircav_1_entity`
- `CZE_mountaineers_0_entity`, `CZE_mountaineers_1_entity`, `CZE_mountaineers_3_entity`
- `DEN_infantry_1_entity` (and variants), `DEN_marine_1_entity`, `DEN_mountaineers_1_entity`, `DEN_airborne_0_entity`, `DEN_airborne_1_entity`, `DEN_aircav_1_entity`
- `EGY_infantry_1_entity` (and variants), `EGY_marine_1_entity`, `EGY_mountaineers_1_entity`, `EGY_airborne_0_entity`, `EGY_airborne_1_entity`, `EGY_aircav_1_entity`
- `GRE_marine_1_entity`, `GRE_mountaineers_1_entity`, `GRE_airborne_0_entity`, `GRE_airborne_1_entity`, `GRE_aircav_1_entity`
- `LUX_infantry_1_entity` (and variants), `LUX_marine_1_entity`, `LUX_mountaineers_1_entity`, `LUX_airborne_0_entity`, `LUX_airborne_1_entity`, `LUX_aircav_1_entity`
- `MAL_infantry_1_entity` (and variants), `MAL_marine_1_entity`, `MAL_mountaineers_1_entity`, `MAL_airborne_1_entity`, `MAL_aircav_1_entity`, `MAL_militia_1_entity`
- `MON_infantry_1_entity`, `MON_mountaineers_0_entity`, `MON_mountaineers_1_entity`, `MON_militia_entity`
- `NGA_marine_1_entity`, `NGA_airborne_0_entity`
- `NOR_infantry_1_entity` (and variants), `NOR_marine_1_entity`, `NOR_mountaineers_1_entity`, `NOR_airborne_0_entity`, `NOR_airborne_1_entity`, `NOR_aircav_1_entity`
- `PDG_mountaineers_1_entity`
- `PHI_marine_1_entity`, `PHI_mountaineers_1_entity`, `PHI_airborne_0_entity`, `PHI_aircav_1_entity`
- `PRC_mountaineers_2_entity`, `PRC_mountaineers_3_entity`
- `RUS_mountaineers_2_entity`, `RUS_mountaineers_3_entity`
- `SAU_infantry_1_entity` (and variants), `SAU_marine_1_entity`, `SAU_mountaineers_1_entity`, `SAU_airborne_0_entity`, `SAU_airborne_1_entity`, `SAU_aircav_1_entity`
- `SAF_infantry_1_entity`
- `SWE_infantry_1_entity`
- `SWI_infantry_1_entity`
- `SYR_infantry_1_entity`
- `TUR_infantry_1_entity`
- `USA_infantry_1_entity`
- `VEN_infantry_1_entity`
- `VIN_infantry_1_entity`
- `WGR_infantry_1_entity` (and variants), `WGR_marine_1_entity`, `WGR_mountaineers_1_entity`, `WGR_airborne_1_entity`, `WGR_aircav_1_entity`
- `YUG_mountaineers_2_entity`, `YUG_mountaineers_3_entity`
- `KRD_mountaineers_2_entity`, `KRD_mountaineers_3_entity`
- `SRT_mountaineers_2_entity`, `SRT_mountaineers_3_entity`

#### Missing "charge_mg" and "charge_mg_shoot" Animations
These entities reference `charge_mg` and `charge_mg_shoot` animations that don't exist in their meshes:
- `CAM_marine_4_entity`
- `CHI_infantry_2_entity` (and variants), `CHI_marine_0_entity`, `CHI_marine_2_entity`, `CHI_mountaineers_2_entity`, `CHI_airborne_2_entity`, `CHI_aircav_2_entity`
- `FRE_paratrooper_4_entity`
- `FRA_infantrymg_2_entity`
- `GRE_infantry_1_entity` (and variants)
- `KMP_infantry_2_entity`, `KMP_infantry_3_entity`, `KMP_infantry_4_entity`, `KMP_marine_0_entity`, `KMP_marine_1_entity`, `KMP_marine_2_entity`, `KMP_marine_3_entity`, `KMP_mountaineers_2_entity`, `KMP_mountaineers_3_entity`, `KMP_airborne_0_entity`, `KMP_airborne_1_entity`
- `KPA_infantry_1_entity`
- `KRD_mountaineers_1_entity`
- `LOS_infantry_2_entity`, `LOS_infantry_3_entity`, `LOS_infantry_4_entity`, `LOS_marine_0_entity`, `LOS_marine_1_entity`, `LOS_marine_2_entity`, `LOS_marine_3_entity`, `LOS_marine_4_entity`
- `MLA_infantry_2_entity`, `MLA_marine_0_entity`, `MLA_marine_1_entity`, `MLA_marine_2_entity`, `MLA_marine_3_entity`, `MLA_mountaineers_2_entity`, `MLA_mountaineers_3_entity`, `MLA_airborne_0_entity`, `MLA_airborne_1_entity`
- `RUS_infantry_1_entity` (and variants)
- `SOV_infantry_1_entity`
- `SPA_infantry_1_entity`
- `UKR_infantry_1_entity`
- `USA_infantry_1_entity`
- `SIK_artillery_inf_0_entity`
- `SRT_infantry_1_entity` (and variants)
- `TIB_infantry_2_entity`, `TIB_mountaineers_0_entity`, `TIB_mountaineers_1_entity`
- `CHK_infantry_2_entity`, `CHK_mountaineers_0_entity`, `CHK_mountaineers_1_entity`
- `HOR_infantry_2_entity`, `HOR_mountaineers_0_entity`, `HOR_mountaineers_1_entity`
- `DER_infantry_2_entity`, `DER_mountaineers_0_entity`, `DER_mountaineers_1_entity`
- `LIN_infantry_2_entity`, `LIN_mountaineers_0_entity`, `LIN_mountaineers_1_entity`
- `NAN_infantry_2_entity`, `NAN_mountaineers_0_entity`, `NAN_mountaineers_1_entity`
- `SAG_infantry_2_entity`, `SAG_mountaineers_0_entity`, `SAG_mountaineers_1_entity`
- `VIE_infantry_2_entity`, `VIE_infantry_3_entity`, `VIE_infantry_4_entity`, `VIE_marine_0_entity`, `VIE_marine_1_entity`, `VIE_marine_2_entity`, `VIE_marine_3_entity`, `VIE_marine_4_entity`
- `YUG_infantry_1_entity` (and variants)

#### Missing Training Animations
These entities reference training animations that don't exist in their meshes:
- `ARG_marine_0_entity`, `ARG_marine_1_entity`, `ARG_airborne_0_entity`, `ARG_airborne_1_entity`: Missing `training`, `jumping_jacks`, `pushup`, `aim_exercise`, `guard_rifle`

#### Missing Vehicle Animations
- `SOV_marine_vehicle_1_entity`: Missing `attack` animation for states `support_attack`, `attack`, and `defend`

**Action Required:**
1. Add the missing animation IDs to the corresponding `pdxmesh` definitions in `.gfx` files, or
2. Remove or replace the animation references in the entity definitions in `.asset` files

---

### 2.4 Missing Sound Effect
**Error:** `Missing sound effect: turbine_engine`

**Status:** UNRESOLVED

**Action Required:** 
1. Create a sound effect definition for `turbine_engine` in an appropriate sound file, or
2. Remove references to `turbine_engine` from entity definitions

---

### 2.5 Missing Entity References
The following entities are referenced but not defined:

- `USA_M113CAMtnam_entity`
- `FRA_infantry_entity`
- `PRC_infantry_weapon_mg_right_entity`
- `USA_M113LOStnam_entity`
- `USA_gfx_infantry_entity`
- `USA_M113VINtnam_entity`
- `FRA_infantry_weapon_rifle_right_entity`
- `FRA_infantry_weapon_rifle_left_entity`
- `FRA_infantry_weapon_rifle_long_idle_entity`
- `USA_cv_CAS_equipment_2_entity` (parent clone entity)

**Action Required:** Create these entity definitions in appropriate `.asset` files

---

### 2.6 Missing Landmark/Building Meshes
The following landmark/building meshes are referenced but not defined:

- `landmark_nanjing_presidential_palace_mesh` (referenced by `building_landmark_nanjing_presidential_palace`)
- `landmark_nanjing_presidential_palace_destroyed_mesh` (referenced by `building_landmark_nanjing_presidential_palace_destroyed`)
- `landmark_nanjing_presidential_palace_prc_mesh` (referenced by `building_landmark_nanjing_presidential_palace_prc`)
- `landmark_nanjing_presidential_palace_prc_destroyed_mesh` (referenced by `building_landmark_nanjing_presidential_palace_prc_destroyed`)

**Note:** These were intentionally commented out as nothing was created for them.

**Action Required:** Either create these meshes or remove the entity references

---

### 2.7 Missing Miscellaneous Meshes
The following meshes are referenced but not defined:

- `bicycle_frame_mesh` (referenced by `bicycle_entity`, `generic_bicycle_2_entity`)
- `bicycle_vehicle_mesh` (referenced by `generic_bicycle_rifle_combined_entity`, `generic_bicycle_vehicle_entity`, `generic_bicycle_mg_combined_entity`)
- `bomber_1_carpetbombing_mesh` (referenced by `bomber_1_carpetbombing_entity`)
- `bomber_3_carpetbombing_mesh` (referenced by `bomber_3_carpetbombing_entity`)
- `bomber_1_firebombing_mesh` (referenced by `bomber_1_firebombing_entity`)
- `bomber_3_firebombing_mesh` (referenced by `bomber_3_firebombing_entity`)

**Action Required:** Create these mesh definitions or update entity references

---

## 3. FILES MODIFIED

The following files were modified during the error fixing process:

### 3.1 Unit/Infantry Files
- `Cold War Iron Curtain/gfx/entities/ARG_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/LOS_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/LEB_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/CUB_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/IRL_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/CHL_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/SAF_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/JAP_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/ETH_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/BRA_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/AUS_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/PRC_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/PRU_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/PER_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/KOR_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/FRA_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/MAL_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/FRE_unit.gfx`
- `Cold War Iron Curtain/gfx/entities/ethnostates_unit.gfx`

### 3.2 Tank Files
- `Cold War Iron Curtain/gfx/entities/tanks.gfx`
- `Cold War Iron Curtain/gfx/entities/USA_tanks.gfx`
- `Cold War Iron Curtain/gfx/entities/CHI_tanks.gfx`
- `Cold War Iron Curtain/gfx/entities/NOR_tanks.gfx`
- `Cold War Iron Curtain/gfx/entities/JOR_tanks.gfx`
- `Cold War Iron Curtain/gfx/entities/EGY_tanks.gfx`
- `Cold War Iron Curtain/gfx/entities/SYR_tanks.gfx`
- `Cold War Iron Curtain/gfx/entities/FIN_tanks.gfx`
- `Cold War Iron Curtain/gfx/entities/DDR_tanks.gfx`
- `Cold War Iron Curtain/gfx/entities/ENG_tanks.gfx`
- `Cold War Iron Curtain/gfx/entities/FRA_tanks.gfx`

### 3.3 Vehicle Files
- `Cold War Iron Curtain/gfx/entities/SOV_vehicles.gfx`
- `Cold War Iron Curtain/gfx/entities/BUL_vehicles.gfx`
- `Cold War Iron Curtain/gfx/entities/DDR_vehicles.gfx`
- `Cold War Iron Curtain/gfx/entities/WGR_vehicles.gfx`

### 3.4 Other Files
- `Cold War Iron Curtain/gfx/entities/00_small_arms.gfx`
- `Cold War Iron Curtain/gfx/entities/NSB_units_trains_meshes.gfx`
- `Cold War Iron Curtain/gfx/entities/ships.gfx`
- `Cold War Iron Curtain/gfx/entities/SOV_plane.gfx`

---

## 4. SUMMARY OF ACTIONS REQUIRED

### High Priority
1. **Create missing mesh definitions** for tank/armor meshes referenced in entity files (Section 2.2)
2. **Fix missing animation references** in entity states (Section 2.3) - Either add animations to meshes or remove references from entities
3. **Create missing entity definitions** (Section 2.5)

### Medium Priority
1. **Create sound effect definition** for `turbine_engine` (Section 2.4)
2. **Create missing landmark/building meshes** or remove references (Section 2.6)
3. **Create missing miscellaneous meshes** (Section 2.7)

### Low Priority
1. **Investigate duplicate animation warning** (Section 2.1) - May be a false positive

---

## 5. NOTES

- All texture-related errors (e.g., `Failed to find texture 'X.dds'`) are not animation-related and are not addressed in this document.
- The Nanjing Presidential Palace entities and animations were intentionally commented out as they were not created.
- IMPORTANT: Many fixes involved using placeholder meshes that are compatible with the existing animations. These should be replaced with proper meshes when available.
- Animation compatibility was ensured by matching joint counts between meshes and animations.

---