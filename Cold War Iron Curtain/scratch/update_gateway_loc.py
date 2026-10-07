import codecs

loc_path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\localisation\english\USA_MKUltra_phase_2_l_english.yml'

with codecs.open(loc_path, 'r', encoding='utf-8-sig') as f:
    text = f.read().replace('\r\n', '\n')

phase5_loc = """
 USA_mkultra_charter_status_army_gateway: "§YArmy INSCOM Operational Charter (Gateway)§!"

 USA_mkultra_commission_gateway_assessment: "Commission the Gateway Assessment"
 USA_mkultra_commission_gateway_assessment_desc: "Authorize a classified technical evaluation of the Gateway Process under U.S. Army INSCOM sponsorship. Explores altered states of consciousness induced by Monroe Institute hemi-sync sound techniques. Costs §Y25 Political Power§!. Adds §R2 Exposure Pressure§! and commits §G0 Harm§!. Completing the 90-day study awards §G14 Research Record§!."
 USA_mkultra_commission_gateway_assessment_tt: "Commit §Y25 Political Power§!, add §R2 Exposure Pressure§!, and begin a 90-day technical evaluation of the Gateway Process."
 USA_mkultra_gateway_assessment_research: "Gateway Process — Laboratory Evaluation Underway"
 USA_mkultra_gateway_assessment_research_desc: "U.S. Army INSCOM analysts and voluntary laboratory subjects are evaluating hemispheric synchronization protocols. Completion awards §G14 Research Record§! and opens the field report."
 USA_mkultra_gateway_assessment_review: "Gateway Process — Review Technical Report"
 USA_mkultra_gateway_assessment_review_desc: "The technical report documents brain-wave frequency response and subjective consciousness alterations under laboratory conditions. Choose whether to commission independent replication or archive findings."
 USA_mkultra_replicate_gateway_assessment: "Commission Independent Scientific Appraisal: Gateway"
 USA_mkultra_replicate_gateway_assessment_desc: "Subject the Gateway findings to independent analytical review by scientific personnel. Costs §Y25 Political Power§! (or §Y35 PP§! under compartmentalization). Adds §R1 Exposure Pressure§!. Completing 60 days of replication awards §G6 Research Record§!."
 USA_mkultra_replicate_gateway_assessment_tt: "Commit Political Power to conduct independent scientific appraisal."
 USA_mkultra_gateway_assessment_replication_research: "Gateway Process — Analytical Appraisal"
 USA_mkultra_gateway_assessment_replication_research_desc: "Independent scientists are reviewing EEG data and examining theoretical models."
 USA_mkultra_gateway_assessment_final_review: "Gateway Process — Final Appraisal"
 USA_mkultra_gateway_assessment_final_review_desc: "Final evaluation concludes that hemispheric synchronization produces reproducible altered subjective states, but fails to demonstrate reliable military intelligence utility."
 USA_mkultra_archive_gateway_assessment: "Archive Gateway Assessment"
 USA_mkultra_archive_gateway_assessment_desc: "File the Gateway documentation in INSCOM technical archives, releasing its research slot."
 USA_mkultra_archive_gateway_assessment_tt: "Archive the dossier and release its slot."

 cwic_mkultra.400.t: "The 1983 Gateway Assessment"
 cwic_mkultra.400.d: "In June 1983, the Operational Group of the U.S. Army Intelligence and Security Command (INSCOM) submitted an assessment of the Gateway Process. Authored by Lieutenant Colonel Wayne M. McDonnell at the request of Army intelligence, the report examines altered states of consciousness induced by the Monroe Institute's hemi-sync sound techniques.\\n\\nMcDonnell's analysis attempts to construct a scientific and philosophical framework for claimed non-local perception. With CIA behavioral programs either closed or heavily curtailed following congressional hearings, Army intelligence requests executive authorization to evaluate whether the methodology warrants classified research or an archive transfer."
 cwic_mkultra.400.a: "Authorize an Army INSCOM evaluation program."
 cwic_mkultra.400.b: "Permit a limited archive transfer for reference only."
 cwic_mkultra.400.c: "Decline authorization; leave past files in storage."
 USA_mkultra_gateway_authorize_tt: "Spend §Y25 Political Power§! to authorize Army INSCOM Gateway research. Closes any lingering CIA charter and grants §G+10 Research Record§! (§G+15§! if earlier files were preserved)."
 USA_mkultra_gateway_archive_transfer_tt: "Spend §Y10 Political Power§! to transfer historical files for reference only, gaining §G+5 Research Record§!."
 USA_mkultra_gateway_decline_tt: "Decline military authorization; the archive remains sealed."

 cwic_mkultra.405.t: "Analysis and Assessment of Gateway Process"
 cwic_mkultra.405.d: "LTC McDonnell's completed assessment synthesizes biomedical models, quantum mechanics, and transcendental meditation theory to explain the Gateway Experience. The document observes that binaural audio beats reliably synchronize hemispheric brain-wave frequencies.\\n\\nHowever, the report notes a fundamental limitation: while laboratory subjects report profound altered states and out-of-body sensations, military application and reliable target acquisition remain entirely unproven."
 cwic_mkultra.405.a: "Commission independent analytical replication."
 cwic_mkultra.405.b: "Archive the assessment in INSCOM technical files."
 USA_mkultra_gateway_replicate_opt_tt: "Authorize scientific replication to verify EEG frequency claims."
 USA_mkultra_gateway_archive_opt_tt: "Archive the findings; laboratory observations are filed without further expenditure."

 cwic_mkultra.420.t: "The Assessment Arrived Early: The Early Memorandum"
 cwic_mkultra.420.d: "The memorandum appears to describe an incident that has not yet occurred. The first analyst has circled the date. The second has circled the distribution list. The sponsor has circled the paragraph recommending continued funding.\\n\\nA contractor research team submits a document describing unusual anomalies coinciding with an impending institutional security scare. The sponsor urges immediate circulation to national defense leadership."
 cwic_mkultra.420.a: "Circulate the memorandum and fund early preparedness."
 cwic_mkultra.420.b: "Commission an independent 90-day analytical appraisal."
 cwic_mkultra.420.c: "Archive the memorandum as an unverified anomaly."
 USA_mkultra_early_assessment_preparedness_tt: "Spend §Y20 Political Power§! and add §R5 Exposure Pressure§! to prepare defensive protocols for an impending event."
 USA_mkultra_early_assessment_appraisal_tt: "Spend §Y30 Political Power§! to commission an independent audit of the contractor's claims and timestamps."
 USA_mkultra_early_assessment_archive_tt: "File the memorandum into the anomalous index without circulating it."

 cwic_mkultra.421.t: "The Assessment Arrived Early: The Matching Event"
 cwic_mkultra.421.d: "Four months after the memorandum was received, a sudden communications switchboard blackout disrupts military circuits, accompanied by false alarms of a foreign technical breakthrough.\\n\\nIn the operations center, staff scramble to verify whether the earlier contractor assessment genuinely foresaw the disruption or whether mundane explanations account for the correlation."
 cwic_mkultra.421.a: "Evaluate the aftermath."

 cwic_mkultra.422.t: "The Assessment Arrived Early: The Final Comparison"
 cwic_mkultra.422.d: "The post-incident case file reviews the episode in retrospect. While the contractor memorandum coincided with the outage, investigators discover that the team had advance access to routine telecommunications maintenance schedules.\\n\\nThe document matched selectively, but failed on specifics. An unsettling file preserved in the classified index."
 cwic_mkultra.422.a: "Archive the completed case file."
 USA_mkultra_early_assessment_comparison_tt: "Resolve the episode, archiving the case file and gaining §G+8 Research Record§!."

 cwic_mkultra.440.t: "The 1995 AIR Review: Research and Applications"
 cwic_mkultra.440.d: "On 29 September 1995, the American Institutes for Research (AIR) completed a comprehensive evaluation of classified anomalous mental phenomena and remote-viewing research, prepared for the Central Intelligence Agency and Department of Defense.\\n\\nThe review makes a rigorous distinction: laboratory experiments showed statistically significant anomalies under specific conditions, but failed to demonstrate actionable operational utility or reliability in military operations.\\n\\nWith the Cold War over and oversight renewed, the administration must decide on the final disposition of consciousness research programs."
 cwic_mkultra.440.a: "Decommission the program and transfer files to civil declassification review."
 cwic_mkultra.440.b: "Retain a sealed, restricted holding under executive privilege."
 USA_mkultra_air_decommission_tt: "Permanently close the research program, reducing Exposure Pressure by §G20§! and gaining §G20 Political Power§!."
 USA_mkultra_air_seal_tt: "Spend §Y15 Political Power§! to keep the archive sealed under executive lock."

 cwic_mkultra.460.t: "Cultural Afterlife: A File Outside Its Setting"
 cwic_mkultra.460.d: "Declassified documents, memoirs by former contractors, and commercialized audio tapes from the Monroe Institute have begun circulating widely in public media. Television broadcasts and books sensationalize decades of secret research.\\n\\nWhile the government maintains official silence, the cultural mythology around MKUltra and military psychic research now takes on a life of its own."
 cwic_mkultra.460.a: "Issue standard 'neither confirm nor deny' statements."
 cwic_mkultra.460.b: "Authorize orderly historical releases under the Freedom of Information Act."
 USA_mkultra_cultural_deny_tt: "Maintain Glomar silence, adding §R2 Exposure Pressure§!."
 USA_mkultra_cultural_foia_tt: "Spend §Y10 Political Power§! to facilitate FOIA disclosures, reducing Exposure Pressure by §G5§!."

 cwic_mkultra.500.t: "The Last Machine in the Records Room"
 cwic_mkultra.500.d: "In January 1999, archivists surveying legacy intelligence systems in preparation for the Year 2000 computer rollover encounter the agency's oldest terminal in the records division. Its software records years using two digits.\\n\\nA covering memorandum notes that decades of classified files—from 1950s BLUEBIRD to MKUltra grants, Midnight Climax vouchers, 1963 MKSEARCH, Church Committee disclosures, and 1983 Gateway assessments—form an indelible, complex record of Cold War anxieties and administrative ambition.\\n\\nAs the new millennium approaches, the institution takes final stock of its accumulated behavioral research."
 cwic_mkultra.500.a: "Seal the final inventory into the permanent national archive."
 USA_mkultra_y2k_epilogue_tt: "Conclude the historical research arc into the permanent national registry."

 USA_mkultra_gui_gateway_assessment_title: "Army INSCOM: The Gateway Assessment"
 USA_mkultra_gui_owner_army_inscom: "U.S. Army INSCOM / Operational Group (Gateway)"
 USA_mkultra_gui_stage_gateway_research: "Technical laboratory evaluation underway"
 USA_mkultra_gui_stage_gateway_report: "Technical report awaiting review"
 USA_mkultra_gui_stage_gateway_replication: "Independent scientific appraisal underway"
 USA_mkultra_gui_stage_gateway_final_report: "Final appraisal awaiting disposition"
 USA_mkultra_gui_selected_stage_gateway_research: "Technical laboratory evaluation underway"
 USA_mkultra_gui_selected_stage_gateway_report: "Technical report awaiting disposition"
 USA_mkultra_gui_selected_stage_gateway_replication: "Independent scientific appraisal underway"
 USA_mkultra_gui_selected_stage_gateway_final_report: "Final appraisal awaiting disposition"
 USA_mkultra_gui_claim_gateway_assessment: "Binaural audio stimulation to induce hemispheric brain-wave synchronization and facilitate altered perception."
 USA_mkultra_gui_gateway_assessment_appraisal: "Rigorous theoretical analysis by LTC McDonnell. Validates altered subjective states under laboratory conditions, but confirms absence of reliable military intelligence utility."
 USA_mkultra_gui_harm_gateway: "§G0 (Voluntary Laboratory Protocol)§!"
 USA_mkultra_gui_commitment_gateway_initial: "Committed: §Y25 PP§! / §R2 Exposure§! / §G0 Harm§!"
 USA_mkultra_gui_commitment_gateway_replicated: "Committed: §Y50 PP§! / §R3 Exposure§! / §G0 Harm§!"
 USA_mkultra_gui_awards_gateway_initial: "§G14§!"
 USA_mkultra_gui_awards_gateway_replicated: "§G20§! (14 initial + 6 replication)"
 USA_mkultra_gui_dimension_gateway_sound: "Binaural audio protocol"
 USA_mkultra_gui_dimension_gateway_coherence: "Hemispheric coherence"
 USA_mkultra_gui_dimension_gateway_nonlocal: "Subjective non-local perception"
 USA_mkultra_gui_dimension_gateway_utility: "Military intelligence utility"
 USA_mkultra_gui_evidence_gateway_sound: "§GMonroe Institute laboratory protocol evaluated§!"
 USA_mkultra_gui_evidence_gateway_coherence: "§YEEG frequency-following response confirmed§!"
 USA_mkultra_gui_evidence_gateway_nonlocal: "§RSubjective reports lack external verification§!"
 USA_mkultra_gui_evidence_gateway_utility: "§RZero operational targeting utility established§!"
 USA_mkultra_gui_application_gateway: "Laboratory consciousness evaluation; no reliable operational targeting or military application demonstrated."
"""

full_content = text + phase5_loc

with open(loc_path, 'wb') as f:
    f.write(codecs.BOM_UTF8)
    f.write(full_content.encode('utf-8'))

print("USA_MKUltra_phase_2_l_english.yml updated with Phase 5 localization and UTF-8 BOM!")
