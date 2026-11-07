# Reviewed land doctrine cell manifest

Finalized 2026-09-05 from uncommented path traversal and active research GUI anchors at HEAD `034c4d0b70` plus the existing working-tree restoration. This is the implementation contract for `Doctrine_Rework_Plan.md`; predecessor entries are the finalized design, not a transcription of old allow blocks.

78 disjoint cells cover 528 technologies; each has exactly one terminal. 67 headers have lineage prerequisites, 70 have date gates, and 11 are independent roots. The 1940 rows have no date gate. All other dates are inclusive January 1. IDs with a different prefix still belong to the cell reached from their GUI anchor.

| GUI x | Decade | Header | Nodes | Terminal | Required predecessor terminal |
| --- | --- | --- | --- | --- | --- |
| 80 | 1940 | `cw_nato_1940s_integrated_arms_reorganization` | 6 | `cw_nato_1940s_early_atomic_support_integration` | **Independent root** |
| 80 | 1950 | `cw_nato_1950s_doctrine_header` | 6 | `cw_nato_1950s_tactical_nuclear_fire_planning` | `cw_nato_1940s_early_atomic_support_integration` |
| 80 | 1960 | `cw_nato_1960s_doctrine_header` | 7 | `cw_nato_1960s_transitional_combined_arms_cohesion` | `cw_nato_1950s_tactical_nuclear_fire_planning` |
| 80 | 1970 | `cw_nato_1970s_doctrine_header` | 7 | `cw_nato_1970s_unified_operational_logistics_backbone` | `cw_nato_1960s_transitional_combined_arms_cohesion` |
| 80 | 1980 | `cw_nato_1980s_doctrine_header` | 7 | `cw_nato_1980s_precision_and_maneuver_synergy` | `cw_nato_1970s_unified_operational_logistics_backbone` |
| 80 | 1990 | `cw_nato_1990s_doctrine_header` | 7 | `cw_nato_1990s_networked_warfare_continuum` | `cw_nato_1980s_precision_and_maneuver_synergy` |
| 560 | 1960 | `cw_sadf_1960s_doctrine_header` | 7 | `cw_sadf_1960s_bush_counter_infiltration_framework` | `cw_nato_1950s_tactical_nuclear_fire_planning` |
| 560 | 1970 | `cw_sadf_1970s_doctrine_header` | 7 | `cw_sadf_1970s_ranger_vertical_assault_synergy` | `cw_sadf_1960s_bush_counter_infiltration_framework` |
| 560 | 1980 | `cw_sadf_1980s_doctrine_header` | 7 | `cw_sadf_1980s_high_mobility_mechanized_fusion` | `cw_sadf_1970s_ranger_vertical_assault_synergy` |
| 560 | 1990 | `cw_sadf_1990s_doctrine_header` | 7 | `cw_sadf_1990s_expeditionary_stabilization_mastery` | `cw_sadf_1980s_high_mobility_mechanized_fusion` |
| 1040 | 1940 | `cw_france_1940s_doctrine_header` | 6 | `cw_france_1940s_tactical_decentralization` | **Independent root** |
| 1040 | 1950 | `cw_france_1950s_doctrine_header` | 6 | `cw_france_1950s_early_professional_force_concepts` | `cw_france_1940s_tactical_decentralization` |
| 1040 | 1960 | `cw_france_1960s_doctrine_header` | 7 | `cw_france_1960s_autonomous_strategic_reform_cohesion` | `cw_france_1950s_early_professional_force_concepts` |
| 1040 | 1970 | `cw_france_1970s_doctrine_header` | 7 | `cw_france_1970s_intervention_maneuver_synergy` | `cw_france_1960s_autonomous_strategic_reform_cohesion` |
| 1040 | 1980 | `cw_france_1980s_doctrine_header` | 7 | `cw_france_1980s_operational_manoeuvre_feu_continuity` | `cw_france_1970s_intervention_maneuver_synergy` |
| 1040 | 1990 | `cw_france_1990s_doctrine_header` | 7 | `cw_france_1990s_digitized_expeditionary_maturation` | `cw_france_1980s_operational_manoeuvre_feu_continuity` |
| 1520 | 1940 | `cw_israel_1940s_doctrine_header` | 6 | `cw_israel_1940s_fragmented_command_coordination` | **Independent root** |
| 1520 | 1950 | `cw_israel_1950s_doctrine_header` | 6 | `cw_israel_1950s_air_ground_coordination_framework` | `cw_israel_1940s_fragmented_command_coordination` |
| 1520 | 1960 | `cw_israel_1960s_doctrine_header` | 7 | `cw_israel_1960s_operational_maneuver_mastery` | `cw_israel_1950s_air_ground_coordination_framework` |
| 1520 | 1970 | `cw_israel_1970s_doctrine_header` | 7 | `cw_israel_1970s_rapid_counteroffensive_adaptation` | `cw_israel_1960s_operational_maneuver_mastery` |
| 1520 | 1980 | `cw_israel_1980s_doctrine_header` | 7 | `cw_israel_1980s_intelligence_driven_operational_synergy` | `cw_israel_1970s_rapid_counteroffensive_adaptation` |
| 1520 | 1990 | `cw_israel_1990s_doctrine_header` | 7 | `cw_israel_1990s_digitized_maneuver_evolution` | `cw_israel_1980s_intelligence_driven_operational_synergy` |
| 2000 | 1940 | `cw_warsaw_1940s_doctrine_header` | 6 | `cw_warsaw_1940s_mechanized_exploitation_forces` | **Independent root** |
| 2000 | 1950 | `cw_warsaw_1950s_doctrine_header` | 6 | `cw_warsaw_1950s_rapid_mobilization_framework` | `cw_warsaw_1940s_mechanized_exploitation_forces` |
| 2000 | 1960 | `cw_warsaw_1960s_doctrine_header` | 7 | `cw_warsaw_1960s_echeloned_assault_refinement` | `cw_warsaw_1950s_rapid_mobilization_framework` |
| 2000 | 1970 | `cw_warsaw_1970s_doctrine_header` | 7 | `cw_warsaw_1970s_offensive_depth_optimization` | `cw_warsaw_1960s_echeloned_assault_refinement` |
| 2000 | 1980 | `cw_warsaw_1980s_doctrine_header` | 7 | `cw_warsaw_1980s_integrated_strike_maneuver_architecture` | `cw_warsaw_1970s_offensive_depth_optimization` |
| 2000 | 1990 | `cw_warsaw_1990s_doctrine_header` | 7 | `cw_warsaw_1990s_high_tech_operational_maturity` | `cw_warsaw_1980s_integrated_strike_maneuver_architecture` |
| 2480 | 1960 | `cw_dprk_1960s_doctrine_header` | 7 | `cw_dprk_1960s_forward_deployed_infiltration_echelons` | `cw_warsaw_1950s_rapid_mobilization_framework` |
| 2480 | 1970 | `cw_dprk_1970s_doctrine_header` | 7 | `cw_dprk_1970s_entrenched_forward_assault_culture` | `cw_dprk_1960s_forward_deployed_infiltration_echelons` |
| 2480 | 1980 | `cw_dprk_1980s_doctrine_header` | 7 | `cw_dprk_1980s_integrated_infiltration_fire_coordination` | `cw_dprk_1970s_entrenched_forward_assault_culture` |
| 2480 | 1990 | `cw_dprk_1990s_doctrine_header` | 7 | `cw_dprk_1990s_fortified_operational_continuity` | `cw_dprk_1980s_integrated_infiltration_fire_coordination` |
| 2960 | 1970 | `cw_cuba_1970s_doctrine_header` | 7 | `cw_cuba_1970s_mobile_combined_arms_proficiency` | `cw_foco_1960s_vanguard_cohesion_doctrine` |
| 2960 | 1980 | `cw_cuba_1980s_doctrine_header` | 7 | `cw_cuba_1980s_operational_sustainment_autonomy` | `cw_cuba_1970s_mobile_combined_arms_proficiency` |
| 2960 | 1990 | `cw_cuba_1990s_doctrine_header` | 7 | `cw_cuba_1990s_revolutionary_vanguard_expeditionism` | `cw_cuba_1980s_operational_sustainment_autonomy` |
| 3440 | 1940 | `cw_prc_1940s_doctrine_header` | 6 | `cw_prc_1940s_political_military_integration` | **Independent root** |
| 3440 | 1950 | `cw_prc_1950s_doctrine_header` | 6 | `cw_prc_1950s_integrated_air_defense_beginnings` | `cw_prc_1940s_political_military_integration` |
| 3440 | 1960 | `cw_prc_1960s_doctrine_header` | 7 | `cw_prc_1960s_peoples_defense_system_consolidation` | `cw_prc_1950s_integrated_air_defense_beginnings` |
| 3440 | 1970 | `cw_prc_1970s_doctrine_header` | 7 | `cw_prc_1970s_layered_territorial_resilience` | `cw_prc_1960s_peoples_defense_system_consolidation` |
| 3440 | 1980 | `cw_prc_1980s_doctrine_header` | 7 | `cw_prc_1980s_reform_era_professional_cohesion` | `cw_prc_1970s_layered_territorial_resilience` |
| 3440 | 1990 | `cw_prc_1990s_doctrine_header` | 7 | `cw_prc_1990s_high_tech_campaign_integration` | `cw_prc_1980s_reform_era_professional_cohesion` |
| 3920 | 1940 | `cw_yugo_1940s_doctrine_header` | 6 | `cw_yugo_1940s_postwar_territorial_defense_blueprint` | **Independent root** |
| 3920 | 1950 | `cw_yugo_1950s_doctrine_header` | 6 | `cw_yugo_1950s_cross_republic_operational_coordination` | `cw_yugo_1940s_postwar_territorial_defense_blueprint` |
| 3920 | 1960 | `cw_yugo_1960s_doctrine_header` | 7 | `cw_yugo_1960s_total_national_resistance_cohesion` | `cw_yugo_1950s_cross_republic_operational_coordination` |
| 3920 | 1970 | `cw_yugo_1970s_doctrine_header` | 7 | `cw_yugo_1970s_distributed_defense_mastery` | `cw_yugo_1960s_total_national_resistance_cohesion` |
| 3920 | 1980 | `cw_yugo_1980s_doctrine_header` | 7 | `cw_yugo_1980s_territorial_command_autonomy` | `cw_yugo_1970s_distributed_defense_mastery` |
| 3920 | 1990 | `cw_yugo_1990s_doctrine_header` | 7 | `cw_yugo_1990s_civil_military_mobilization_continuum` | `cw_yugo_1980s_territorial_command_autonomy` |
| 4400 | 1960 | `cw_himalayan_1960s_doctrine_header` | 6 | `cw_himalayan_1960s_riverine_and_marsh_defense_methods` | **Independent root** |
| 4400 | 1970 | `cw_himalayan_1970s_doctrine_header` | 7 | `cw_himalayan_1970s_operational_bifurcation_mastery` | `cw_himalayan_1960s_riverine_and_marsh_defense_methods` |
| 4400 | 1980 | `cw_himalayan_1980s_doctrine_header` | 7 | `cw_himalayan_1980s_extreme_terrain_hardening` | `cw_himalayan_1970s_operational_bifurcation_mastery` |
| 4400 | 1990 | `cw_himalayan_1990s_doctrine_header` | 7 | `cw_himalayan_1990s_frontline_modernization_cohesion` | `cw_himalayan_1980s_extreme_terrain_hardening` |
| 4880 | 1940 | `cw_non_aligned_1940s_doctrine_header` | 6 | `cw_non_aligned_1940s_integrated_defense_concept` | **Independent root** |
| 4880 | 1950 | `cw_non_aligned_1950s_doctrine_header` | 6 | `cw_non_aligned_1950s_1950s_consolidated_doctrine` | `cw_non_aligned_1940s_integrated_defense_concept` |
| 4880 | 1960 | `cw_non_aligned_1960s_doctrine_header` | 7 | `cw_non_aligned_1960s_localized_strategic_adaptation` | `cw_non_aligned_1950s_1950s_consolidated_doctrine` |
| 4880 | 1970 | `cw_non_aligned_1970s_doctrine_header` | 7 | `cw_non_aligned_1970s_nationalized_command_evolution` | `cw_non_aligned_1960s_localized_strategic_adaptation` |
| 4880 | 1980 | `cw_non_aligned_1980s_doctrine_header` | 7 | `cw_non_aligned_1980s_modernization_pipeline_optimization` | `cw_non_aligned_1970s_nationalized_command_evolution` |
| 4880 | 1990 | `cw_non_aligned_1990s_doctrine_header` | 7 | `cw_non_aligned_1990s_professional_combat_readiness` | `cw_non_aligned_1980s_modernization_pipeline_optimization` |
| 5360 | 1980 | `cw_iran_1980s_doctrine_header` | 6 | `cw_iran_1980s_forward_defense_in_depth` | **Independent root** |
| 5360 | 1990 | `cw_iran_1990s_doctrine_header` | 7 | `cw_iran_1990s_revolutionary_hybrid_force_consolidation` | `cw_iran_1980s_forward_defense_in_depth` |
| 5840 | 1960 | `cw_maoist_1960s_doctrine_header` | 7 | `cw_maoist_1960s_revolutionary_continuity_bonds` | `cw_ins_1950s_protracted_war_planning_doctrine` |
| 5840 | 1970 | `cw_maoist_1970s_doctrine_header` | 7 | `cw_maoist_1970s_consolidated_base_area_administration` | `cw_maoist_1960s_revolutionary_continuity_bonds` |
| 5840 | 1980 | `cw_maoist_1980s_doctrine_header` | 7 | `cw_maoist_1980s_advanced_guerrilla_layering_techniques` | `cw_maoist_1970s_consolidated_base_area_administration` |
| 5840 | 1990 | `cw_maoist_1990s_doctrine_header` | 7 | `cw_maoist_1990s_adaptive_survival_governance` | `cw_maoist_1980s_advanced_guerrilla_layering_techniques` |
| 6320 | 1960 | `cw_foco_1960s_doctrine_header` | 7 | `cw_foco_1960s_vanguard_cohesion_doctrine` | `cw_ins_1950s_protracted_war_planning_doctrine` |
| 6320 | 1970 | `cw_foco_1970s_doctrine_header` | 7 | `cw_foco_1970s_agitation_action_continuum` | `cw_foco_1960s_vanguard_cohesion_doctrine` |
| 6320 | 1980 | `cw_foco_1980s_doctrine_header` | 7 | `cw_foco_1980s_clandestine_cell_refinement` | `cw_foco_1970s_agitation_action_continuum` |
| 6320 | 1990 | `cw_foco_1990s_doctrine_header` | 7 | `cw_foco_1990s_surviving_vanguard_legacy` | `cw_foco_1980s_clandestine_cell_refinement` |
| 6800 | 1940 | `cw_ins_1940s_doctrine_header` | 6 | `cw_ins_1940s_integrated_liberation_movement_framework` | **Independent root** |
| 6800 | 1950 | `cw_ins_1950s_doctrine_header` | 6 | `cw_ins_1950s_protracted_war_planning_doctrine` | `cw_ins_1940s_integrated_liberation_movement_framework` |
| 6800 | 1960 | `cw_hybrid_ins_1960s_doctrine_header` | 7 | `cw_hybrid_ins_1960s_early_fusion_doctrine_refinement` | `cw_ins_1950s_protracted_war_planning_doctrine` |
| 6800 | 1970 | `cw_hybrid_ins_1970s_doctrine_header` | 7 | `cw_hybrid_ins_1970s_integrated_regional_councils` | `cw_hybrid_ins_1960s_early_fusion_doctrine_refinement` |
| 6800 | 1980 | `cw_hybrid_ins_1980s_doctrine_header` | 7 | `cw_hybrid_ins_1980s_sustained_logistics_corridors` | `cw_hybrid_ins_1970s_integrated_regional_councils` |
| 6800 | 1990 | `cw_hybrid_ins_1990s_doctrine_header` | 7 | `cw_hybrid_ins_1990s_semi_conventional_stability` | `cw_hybrid_ins_1980s_sustained_logistics_corridors` |
| 7280 | 1960 | `cw_islamist_ins_1960s_doctrine_header` | 7 | `cw_islamist_ins_1960s_clerical_network_consolidation` | `cw_ins_1950s_protracted_war_planning_doctrine` |
| 7280 | 1970 | `cw_islamist_ins_1970s_doctrine_header` | 7 | `cw_islamist_ins_1970s_ideological_foundation_maturation` | `cw_islamist_ins_1960s_clerical_network_consolidation` |
| 7280 | 1980 | `cw_islamist_ins_1980s_doctrine_header` | 7 | `cw_islamist_ins_1980s_external_support_integration` | `cw_islamist_ins_1970s_ideological_foundation_maturation` |
| 7280 | 1990 | `cw_islamist_ins_1990s_doctrine_header` | 7 | `cw_islamist_ins_1990s_localized_emirate_governance` | `cw_islamist_ins_1980s_external_support_integration` |
| 7760 | 1990 | `cw_islamist_alt_ins_1990s_doctrine_header` | 7 | `cw_islamist_ins_1990s_global_operational_continuum` | **Independent root** |
