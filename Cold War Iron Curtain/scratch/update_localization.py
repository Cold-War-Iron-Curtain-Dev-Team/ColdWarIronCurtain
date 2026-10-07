import codecs

loc_path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\localisation\english\USA_MKUltra_phase_2_l_english.yml'

with codecs.open(loc_path, 'r', encoding='utf-8-sig') as f:
    text = f.read().replace('\r\n', '\n')

new_loc = """
 USA_mkultra_charter_status_expanded: "§GExpanded Charter (2 Research Slots)§!"
 USA_mkultra_slot_status_dual: "[GetUSA_MKUltraSlot1Status] | [GetUSA_MKUltraSlot2Status]"
 USA_mkultra_expand_charter_capacity: "Expand Authorization: Two Active Research Slots"
 USA_mkultra_expand_charter_capacity_desc: "Expand the research charter to support concurrent dossiers. Requires §Y30 Research Record§!, at least two completed initial studies, one reviewed report, and no active inquiry. Costs §Y60 Political Power§!. Expanding authorization unlocks §YSlot Two§!; however, all subsequent studies, renewals, and replications incur a per-stage surcharge of §Y+5 Political Power§! and commit §R+1 Exposure Pressure§!."
 USA_mkultra_expand_charter_capacity_tt: "Spend §Y60 Political Power§! to expand the charter to §G2 active research slots§!. Subsequent stages incur a §Y+5 PP§! surcharge and commit §R+1 Exposure§!."
 USA_mkultra_policy_compartmentalization: "Adopt Strict Compartmentalization Policy"
 USA_mkultra_policy_compartmentalization_desc: "Enforce strict compartmentalization across research contracts. Costs §Y20 Political Power§!. Reduces future study and renewal exposure commitments by §G2§! (minimum 1), while independent replication costs increase by §R10 Political Power§!."
 USA_mkultra_policy_compartmentalization_tt: "Spend §Y20 Political Power§!. Future studies and renewals commit §G-2 Exposure Pressure§! (min 1); independent replications cost §R+10 PP§!."
 USA_mkultra_policy_shared_review: "Restore Shared Inter-Agency Review Policy"
 USA_mkultra_policy_shared_review_desc: "Return to standard inter-agency shared review. Costs §Y10 Political Power§!, restoring baseline exposure increments and standard replication costs."
 USA_mkultra_policy_shared_review_tt: "Spend §Y10 Political Power§! to return to shared inter-agency review."

 USA_mkultra_precursor_brief: "Review Precursor Files: Project BLUEBIRD & ARTICHOKE"
 USA_mkultra_precursor_brief_desc: "Review early 1950-1951 behavioral conditioning and interrogation dossiers compiled under Projects BLUEBIRD and ARTICHOKE. Costs §Y10 Political Power§!. Awards §G+5 Research Record§! and §R+1 Exposure Pressure§!."
 USA_mkultra_precursor_brief_tt: "Spend §Y10 Political Power§! to review precursor files, gaining §G+5 Research Record§! and §R+1 Exposure Pressure§!."

 cwic_mkultra.101.t: "Projects BLUEBIRD and ARTICHOKE"
 cwic_mkultra.101.d: "Before the formal authorization of Project MKUltra, the Agency conducted exploratory behavioral and interrogation studies under the code names BLUEBIRD (1950) and ARTICHOKE (1951). Initiated under Director Roscoe Hillenkoetter and expanded under Walter Bedell Smith, these programs evaluated whether foreign services could establish involuntary behavioral control or extract classified information during interrogation.\\n\\nThe precursor files reveal early experiments in hypnosis, chemical narcosis, and psychological isolation. While inconclusive, the documentation provides the institutional foundation for expanding domestic behavioral research."
 cwic_mkultra.101.a: "Log the findings in the central registry."

 cwic_mkultra.310.t: "A Larger Remit: Expanded Charter Authorization"
 cwic_mkultra.310.d: "The program's work now involves enough offices that no single office can explain the entire program. Its sponsors regard this as evidence of national importance. The administrative review regards it as a reason to assign another administrator.\\n\\nWith executive approval granted, Project MKUltra is authorized to maintain two concurrent research dossiers. However, coordinating expanded contractor networks increases operational overhead and exposure risks."
 cwic_mkultra.310.a: "Authorize the second project slot."

 USA_mkultra_commission_midnight_climax: "Commission Operation Midnight Climax"
 USA_mkultra_commission_midnight_climax_desc: "Establish covert safehouses in San Francisco and New York to study the behavioral effects of chemical agents on unwitting subjects under simulated operational conditions. Costs §Y25 Political Power§!. Commitment adds §R8 Exposure Pressure§! and commits §R8 Recorded Harm/Liability§!. Completing the 90-day study awards §G16 Research Record§!."
 USA_mkultra_commission_midnight_climax_tt: "Commit §Y25 Political Power§!, add §R8 Exposure Pressure§!, commit §R8 Harm/Liability§!, and begin a 90-day safehouse trial."
 USA_mkultra_midnight_climax_research: "Operation Midnight Climax — Field Trials Underway"
 USA_mkultra_midnight_climax_research_desc: "Covert safehouses are actively operating under the direction of the Technical Services Staff. At the end of §Y90 days§!, completion awards §G16 Research Record§! and opens the field report."
 USA_mkultra_midnight_climax_review: "Operation Midnight Climax — Review Field Report"
 USA_mkultra_midnight_climax_review_desc: "The field report documents extensive administration of chemical compounds to unwitting subjects. The operational utility remains contentious while legal and ethical liabilities are acute.\\n\\nWithin §Y30 days§!, choose whether to authorize renewal, commission independent oversight, or archive the dossier."
 USA_mkultra_renew_midnight_climax: "Authorize Renewal: Operation Midnight Climax"
 USA_mkultra_renew_midnight_climax_desc: "Continue covert safehouse operations for another 90 days. Costs §Y25 Political Power§!. Commitment adds §R8 Exposure Pressure§! and §R8 Recorded Harm/Liability§!. Completing renewal awards §G6 Research Record§!."
 USA_mkultra_renew_midnight_climax_tt: "Commit §Y25 Political Power§!, add §R8 Exposure Pressure§!, and commit §R8 Harm/Liability§!."
 USA_mkultra_midnight_climax_renewal_research: "Operation Midnight Climax — Extended Safehouse Trials"
 USA_mkultra_midnight_climax_renewal_research_desc: "Extended safehouse operations are underway. Completion awards §G6 Research Record§! and opens the renewed field report."
 USA_mkultra_midnight_climax_renewal_review: "Operation Midnight Climax — Review Extended Report"
 USA_mkultra_midnight_climax_renewal_review_desc: "Review extended safehouse findings. Choose whether to commission independent replication or archive the report."
 USA_mkultra_replicate_midnight_climax: "Commission Independent Review: Midnight Climax"
 USA_mkultra_replicate_midnight_climax_desc: "Subject the safehouse documentation to internal analytical review. Costs §Y30 Political Power§! (or §Y40 PP§! under compartmentalization). Adds §R1 Exposure Pressure§! and §G0 Harm§!. Completion awards §G6 Research Record§!."
 USA_mkultra_replicate_midnight_climax_tt: "Commit Political Power to conduct independent review of safehouse data."
 USA_mkultra_midnight_climax_replication_research: "Operation Midnight Climax — Analytical Review"
 USA_mkultra_midnight_climax_replication_research_desc: "Analysts are auditing safehouse documentation and testing validity of reported findings."
 USA_mkultra_midnight_climax_final_review: "Operation Midnight Climax — Final Appraisal"
 USA_mkultra_midnight_climax_final_review_desc: "Final evaluation concludes that safehouse trials produced acute legal exposure without establishing reliable behavioral control."
 USA_mkultra_archive_midnight_climax: "Archive Operation Midnight Climax"
 USA_mkultra_archive_midnight_climax_desc: "Close and archive the safehouse dossier, releasing its research slot."
 USA_mkultra_archive_midnight_climax_tt: "Archive the dossier and release its slot."

 cwic_mkultra.300.t: "The Inspector General's Audit"
 cwic_mkultra.300.d: "In 1963, CIA Inspector General John Earman concluded a comprehensive internal audit of Project MKUltra. The report warns that testing substances on unwitting human subjects is 'unethical and unconstitutional,' leaving the Agency exposed to severe public condemnation should the activities be discovered.\\n\\nEarman recommends immediate executive intervention: either formally reorganizing the program under tighter scientific oversight or enforcing director-level operational controls."
 cwic_mkultra.300.a: "Reorganize the program into Project MKSEARCH."
 cwic_mkultra.300.b: "Enforce strict internal administrative controls."
 USA_mkultra_ig_review_mksearch_tt: "Reorganize research into MKSEARCH, phasing out safehouses and reducing Exposure Pressure by §G15§!."
 USA_mkultra_ig_review_tighten_tt: "Spend §Y15 Political Power§! to tighten administrative oversight, reducing Exposure Pressure by §G10§!."

 cwic_mkultra.320.t: "The Records Disposition Order"
 cwic_mkultra.320.d: "With the resignation of Director Richard Helms in January 1973, executive leadership faces a critical decision regarding the accumulated files of Project MKUltra and related programs. Decades of sensitive contractor grants, biological caches, and unwitting trial records fill Agency archives.\\n\\nHelms and scientific director Sidney Gottlieb confer on the disposition of the files. The choices carry profound consequences for future institutional and public accountability."
 cwic_mkultra.320.a: "Preserve and inventory all working files."
 cwic_mkultra.320.b: "Seal holdings for restricted executive retention."
 cwic_mkultra.320.c: "Order the destruction of all working files."
 cwic_mkultra.320.d: "Retain current holdings without taking action."
 USA_mkultra_records_preserve_tt: "Spend §Y10 Political Power§! and add §R5 Exposure Pressure§! to preserve the full historical archive."
 USA_mkultra_records_seal_tt: "Spend §Y15 Political Power§! and reduce Exposure Pressure by §G5§! to seal all holdings under executive lock."
 USA_mkultra_records_destroy_tt: "Spend §Y5 Political Power§! and reduce Exposure Pressure by §G10§!. Working files are burned; however, external and financial records may survive."
 USA_mkultra_records_retain_tt: "Spend §G0 Political Power§! to leave existing holdings in place."

 cwic_mkultra.325.t: "Congressional Scrutiny: The Church Committee"
 cwic_mkultra.325.d: "In 1975, following press revelations by Seymour Hersh regarding domestic intelligence abuses, President Ford appoints the Rockefeller Commission and the Senate creates the Church Committee chaired by Senator Frank Church.\\n\\nInvestigators subpoena Agency records regarding biological testing and behavioral modification. The resulting hearings subject the intelligence community to unprecedented public scrutiny, formally terminating any remaining active covert research charters."
 cwic_mkultra.325.a: "Cooperate with the congressional committees."
 USA_mkultra_church_committee_tt: "Spend §R50 Political Power§!, lose §R2% Stability§!, reduce Exposure Pressure by §G15§!, and permanently terminate any active charter."

 cwic_mkultra.330.t: "Surviving Invoices: The 1977 Senate Hearings"
 cwic_mkultra.330.d: "The research files were thought to be gone. However, in 1977, an archivist in the Budget and Finance division discovered seven boxes containing over 20,000 financial vouchers and invoices that had escaped the 1973 destruction order.\\n\\nThe surviving documents connect specific payments to university foundations, hospitals, and prison facilities, providing undeniable proof of the program's scope. Senator Ted Kennedy convenes joint Senate hearings to examine the newly uncovered financial trail."
 cwic_mkultra.330.a: "Testify before the joint committee."
 USA_mkultra_senate_hearing_tt: "Spend §R25 Political Power§!, lose §R1% Stability§!, and reduce Exposure Pressure by §G10§!."

 USA_mkultra_gui_midnight_climax_title: "Special Operations: Midnight Climax"
 USA_mkultra_gui_commitment_midnight_initial: "Committed: §Y25 PP§! / §R8 Exposure§! / §R8 Harm§!"
 USA_mkultra_gui_commitment_midnight_renewed: "Committed: §Y50 PP§! / §R16 Exposure§! / §R16 Harm§!"
 USA_mkultra_gui_commitment_midnight_replicated: "Committed: §Y55 PP§! / §R9 Exposure§! / §R8 Harm§!"
 USA_mkultra_gui_commitment_midnight_full: "Committed: §Y80 PP§! / §R17 Exposure§! / §R16 Harm§!"
 USA_mkultra_gui_owner_cia_midnight: "CIA Directorate of Plans / TSS Safehouse Network"
 USA_mkultra_gui_selected_stage_midnight_research: "Initial safehouse operation underway"
 USA_mkultra_gui_selected_stage_midnight_report: "Field report awaiting disposition"
 USA_mkultra_gui_selected_stage_midnight_renewal_research: "Extended safehouse renewal underway"
 USA_mkultra_gui_selected_stage_midnight_renewal_report: "Renewal field report awaiting disposition"
 USA_mkultra_gui_selected_stage_midnight_replication: "Analytical review / replication underway"
 USA_mkultra_gui_selected_stage_midnight_final_report: "Final analytical appraisal awaiting disposition"
 USA_mkultra_gui_claim_midnight_climax: "Covert safehouses administering chemical substances to unwitting individuals to test behavioral incapacitation and interrogation vulnerability."
 USA_mkultra_gui_midnight_climax_appraisal: "High-risk operational trials with severe ethical liability and acute exposure vulnerability. Records are heavily compartmented."
 USA_mkultra_gui_harm_midnight_initial: "§R+8 (Acute Liability)§!"
 USA_mkultra_gui_harm_midnight_renewed: "§R+16 (Severe Liability)§!"
 USA_mkultra_gui_awards_midnight_initial: "§G16§!"
 USA_mkultra_gui_awards_midnight_renewed: "§G22§! (16 initial + 6 renewal)"
 USA_mkultra_gui_awards_midnight_replicated: "§G22§! (16 initial + 6 replication)"
 USA_mkultra_gui_awards_midnight_full: "§G28§! (16 initial + 6 renewal + 6 replication)"
 USA_mkultra_gui_dimension_midnight_infra: "Safehouse infrastructure"
 USA_mkultra_gui_dimension_midnight_subjects: "Subject vulnerability"
 USA_mkultra_gui_dimension_midnight_chemicals: "Chemical administration logs"
 USA_mkultra_gui_dimension_midnight_vouchers: "Financial vouchers"
 USA_mkultra_gui_evidence_midnight_infra: "§YEstablished in San Francisco and New York§!"
 USA_mkultra_gui_evidence_midnight_subjects: "§RUnwitting civilian testing documented§!"
 USA_mkultra_gui_evidence_midnight_chemicals: "§YPartial dosage and reaction logs§!"
 USA_mkultra_gui_evidence_midnight_vouchers: "§GPreserved in Budget and Finance archives§!"
 USA_mkultra_gui_application_midnight: "Tactical interrogation and incapacitation observations; no durable operational mind control was established."
"""

full_content = text + new_loc

# Save with UTF-8 BOM
with open(loc_path, 'wb') as f:
    f.write(codecs.BOM_UTF8)
    f.write(full_content.encode('utf-8'))

print("USA_MKUltra_phase_2_l_english.yml updated with BOM!")
