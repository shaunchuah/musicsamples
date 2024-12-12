# Mini-MUSIC

```py title="assets/mini_music.py"
import numpy as np
import pandas as pd
import requests
from dagster import (
    AssetExecutionContext,
    EnvVar,
    MaterializeResult,
    MetadataValue,
    asset,
)

from music_dagster.resources import GTracResource


@asset(
    description="Fetches Mini-MUSIC data from IGMM RedCap Server",
    group_name="mini_music",
)
def mini_music_raw_dataframe(context: AssetExecutionContext) -> pd.DataFrame:
    MINI_MUSIC_API_TOKEN = EnvVar("MINI_MUSIC_API_TOKEN").get_value()
    mini_music_redcap_url = "https://ecrf.igmm.ed.ac.uk/api/"
    redcap_api_data = {
        "token": f"{MINI_MUSIC_API_TOKEN}",
        "content": "record",
        "action": "export",
        "format": "json",
        "type": "flat",
        "csvDelimiter": "",
        "forms[0]": "patient_details",
        "forms[1]": "diagnosis",
        "forms[2]": "timepoints",
        "forms[3]": "phenotyping",
        "forms[4]": "current_drug_treatment",
        "forms[5]": "endoscopic_disease_activity",
        "forms[6]": "radiologic_disease_activity",
        "forms[7]": "surgical_intervention",
        "forms[8]": "saliva_sample",
        "forms[9]": "laboratory_tests_for_disease_activity",
        "forms[10]": "impact_iiipromis_fatigue_score",
        "rawOrLabel": "raw",
        "rawOrLabelHeaders": "raw",
        "exportCheckboxLabel": "false",
        "exportSurveyFields": "false",
        "exportDataAccessGroups": "false",
        "returnFormat": "json",
    }
    response = requests.post(mini_music_redcap_url, data=redcap_api_data)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame.from_records(data)

    df.drop(
        columns=[
            "redcap_repeat_instrument",
            "redcap_repeat_instance",
            "study_name",
            "other_site",
            "consent_point8",
            "assent_type",
            "consent_type___1",
            "consent_type___2",
            "consent_type____1000",
            "pis_type___1",
            "pis_type___2",
            "pis_type___3",
            "pis_type___4",
            "pis_type____1000",
            "date_data_entry",
            "consent_date",
            "consenter_initial",
            "recruitment_setting",
            "consenter_initials",
            "assent_version",
            "consent_version",
            "patient_pis_version",
            "parent_pis_version",
            "parent_pis_yn",
            "patient_pis_yn",
            "gp_yn",
            "par_tel_no",
            "parent_email",
            "chi_no",
            "initial",
            "dob",
            "patient_email",
            "pat_tel_no",
            "patdetailscomments",
            "fuvisit_yn",
            "patient_details_complete",
            "diagnosis_complete",
            "unit_bilirubin",
            "unit_potassium",
            "unit_sodium",
            "unit_creatinine",
            "unit_urea",
            "unit_plt",
            "unit_basophils",
            "unit_eosinophils",
            "unit_monocytes",
            "unit_lymphocytes",
            "unit_neutrophils",
            "unit_wcc",
            "unit_haematocrit",
            "unit_hb",
            "unit_mcv",
            "drug_level_vedo",
            "drug_level_antibody_vedo",
            "drug_level_uste",
            "drug_level_antibody_uste",
            "vedolizumab_level",
            "ustekinumab_level",
            "surgical_intervention_complete",
            "radiologic_disease_activity_complete",
            "type_eim____1000",
            "baseline_symptoms_desc2____1000",
            "visit1",
            "timepoints_complete",
            "flare_up_description1____1000",
            "flare_up_description2____1000",
            "flare_up_management1____1000",
            "flare_up_management2____1000",
            "unplanned_hospital_reason1____1000",
            "unplanned_hospital_reason2____1000",
            "baseline_eims___99",
            "baseline_eims____1000",
            "baseline_eims_subother____1000",
            "baseline_surgical_history",
            "baseline_ibd_drug_entry",
            "baseline_ibd_date_1",
            "mh_any",
            "mh_num",
            "mh_system1",
            "mh_term_other1",
            "mh_system2",
            "mh_term_other2",
            "mh_system3",
            "mh_term_other3",
            "mh_system4",
            "mh_term_other4",
            "mh_system5",
            "mh_term_other5",
            "mh_system6",
            "mh_term_other6",
            "mh_system7",
            "mh_term_other7",
            "phenotyping_complete",
            "other_endoscopy_type____1000",
            "endoscopic_score",
            "endoscopy_yn",
            "endoscopy_type___1",
            "endoscopy_type____1000",
            "other_endoscopy_type___4",
            "other_endoscopy_type___5",
            "other_endoscopy_type___6",
            "other_endoscopy_type____1000",
            "upload_endoscopic_image",
            "uceisvascular_pattern",
            "uceisbleeding",
            "uceiserosions_and_ulcers",
            "score_ileum",
            "score_right",
            "score_transverse",
            "score_left",
            "score_rectum",
            "endoscopic_disease_activity_complete",
            "radiology",
            "mrisb_image",
            "saliva_sample_complete",
            "adalimumab_level",
            "infliximab_level",
            "vedolizumab_level",
            "ustekinumab_level",
            "otherdruglevel",
            "laboratory_tests_for_disease_activity_complete",
            "impact_iiipromis_fatigue_score_complete",
            "meds_summary____1000",
            "current_drug_treatment_complete",
        ],
        inplace=True,
    )
    rows, columns = df.shape
    context.add_output_metadata(
        {
            "dagster/row_count": rows,
            "column_count": columns,
        }
    )
    return df


@asset(
    description="Performs data cleaning on Mini-MUSIC data",
    group_name="mini_music",
)
def mini_music_cleaned_dataframe(
    context: AssetExecutionContext, mini_music_raw_dataframe: pd.DataFrame
) -> pd.DataFrame:
    df = mini_music_raw_dataframe

    df.rename(
        columns={
            "haematocrit_lab": "haematocrit",
            "neutrophils_lab": "neutrophils",
            "lymphocytes_lab": "lymphocytes",
            "monocytes_lab": "monocytes",
            "eosinophils_lab": "eosinophils",
            "basophils_lab": "basophils",
            "plt_lab": "platelets",
            "bilirubin_lab": "bilirubin",
            "urea_lab": "urea",
            "creatinine_lab": "creatinine",
            "sodium_lab": "sodium",
            "potassium_lab": "potassium",
            "diagnosis_comment": "diagnosis_comments",
            "flare_up_timeframe1": "flare_up_1_date",
            "flare_up_description1___1": "flare_up_1_description_abdominal_pain",
            "flare_up_description1___2": "flare_up_1_description_diarrhoea",
            "flare_up_description1___3": "flare_up_1_description_urgency",
            "flare_up_description1___4": "flare_up_1_description_pr_bleeding",
            "flare_up_description1___5": "flare_up_1_description_weight_loss",
            "flare_up_description1___6": "flare_up_1_description_fever",
            "flare_up_description1___7": "flare_up_1_description_perianal",
            "flare_setting1": "flare_up_1_setting",
            "flare_setting2": "flare_up_2_setting",
            "flare_up_management1___1": "flare_up_1_management_iv_steroids",
            "flare_up_management1___3": "flare_up_1_management_oral_steroids",
            "flare_up_management1___5": "flare_up_1_management_een",
            "flare_up_management1___6": "flare_up_1_management_new_biologic",
            "flare_up_management1___99": "flare_up_1_management_other",
            "flare_up_management_other1": "flare_up_1_management_other_text",
            "flare_up_timeframe2": "flare_up_2_date",
            "flare_up_description2___1": "flare_up_2_description_abdominal_pain",
            "flare_up_description2___2": "flare_up_2_description_diarrhoea",
            "flare_up_description2___3": "flare_up_2_description_urgency",
            "flare_up_description2___4": "flare_up_2_description_pr_bleeding",
            "flare_up_description2___5": "flare_up_2_description_weight_loss",
            "flare_up_description2___6": "flare_up_2_description_fever",
            "flare_up_description2___7": "flare_up_2_description_perianal",
            "flare_up_management2___1": "flare_up_2_management_iv_steroids",
            "flare_up_management2___3": "flare_up_2_management_oral_steroids",
            "flare_up_management2___5": "flare_up_2_management_een",
            "flare_up_management2___6": "flare_up_2_management_new_biologic",
            "flare_up_management2___99": "flare_up_2_management_other",
            "flare_up_management_other2": "flare_up_2_management_other_text",
            "unplanned_hospital": "unplanned_hospital_admission",
            "flare_up_comment": "flare_up_comments",
            "reason_of_use_steroid1": "steroid_use_1_reason",
            "other_reason_use_steroid1": "steroid_use_1_reason_text",
            "steroid_type_cu1": "steroid_use_1_drug",
            "steroid_other_drug_cu1": "steroid_use_1_drug_text",
            "steroid_startdate1": "steroid_use_1_start_date",
            "still_taken_steroid1": "steroid_use_1_still_taking",
            "steroid_enddate1": "steroid_use_1_end_date",
            "stop_steroid_res1": "steroid_use_1_reason_stopped",
            "steroid_change_dose1": "steroid_use_1_reason_changed",
            "other_stop_steroid_res1": "steroid_use_1_reason_changed_text",
            "reason_of_use_steroid2": "steroid_use_2_reason",
            "other_reason_use_steroid2": "steroid_use_2_reason_text",
            "steroid_type_cu2": "steroid_use_2_drug",
            "steroid_other_drug_cu2": "steroid_use_2_drug_text",
            "steroid_startdate2": "steroid_use_2_start_date",
            "still_taken_steroid2": "steroid_use_2_still_taking",
            "steroid_enddate2": "steroid_use_2_end_date",
            "steroid_stop_reason2": "steroid_use_2_reason_stopped",
            "steroid_change_dose2": "steroid_use_2_reason_changed",
            "other_steroid_stop_reason2": "steroid_use_2_reason_changed_text",
            "unplanned_hospital_reason1___1": "hospital_admission_1_for_acute_severe_colitis",
            "unplanned_hospital_reason1___2": "hospital_admission_1_for_ibd_flare_not_asc",
            "unplanned_hospital_reason1___3": "hospital_admission_1_for_perianal_disease",
            "unplanned_hospital_reason1___4": "hospital_admission_1_for_surgery",
            "unplanned_hospital_reason1___5": "hospital_admission_1_for_investigation_not_meeting_other_criteria",
            "unplanned_hospital_reason1___99": "hospital_admission_1_for_other",
            "unplan_adm_hosp_other1": "hospital_admission_1_for_other_text",
            "unplaned_hos_adm_date1": "hospital_admission_1_admission_date",
            "hospital_discharge_date1": "hospital_admission_1_discharge_date",
            "unplanned_hospital_reason2___1": "hospital_admission_2_for_acute_severe_colitis",
            "unplanned_hospital_reason2___2": "hospital_admission_2_for_ibd_flare_not_asc",
            "unplanned_hospital_reason2___3": "hospital_admission_2_for_perianal_disease",
            "unplanned_hospital_reason2___4": "hospital_admission_2_for_surgery",
            "unplanned_hospital_reason2___5": "hospital_admission_2_for_investigation_not_meeting_other_criteria",
            "unplanned_hospital_reason2___99": "hospital_admission_2_for_other",
            "unplan_adm_hosp_other2": "hospital_admission_2_for_other_text",
            "unplaned_hos_adm_date2": "hospital_admission_2_admission_date",
            "hospital_discharge_date2": "hospital_admission_2_discharge_date",
            "unplanned_hospital_comment": "hospital_admission_comments",
            "dt_current_ibd_steroid": "new_oral_steroids_since_last_visit",
            "baseline_drug_check": "baseline_previous_ibd_treatment",
            "baseline_eims___1": "baseline_eims_none",
            "baseline_eims___2": "baseline_eims_arthritis",
            "baseline_eims___5": "baseline_eims_erythema_nodosum",
            "baseline_eims___6": "baseline_eims_pyoderma",
            "baseline_eims___10": "baseline_eims_uveitis",
            "baseline_eims___12": "baseline_eims_episcleritis",
            "baseline_eims_subother___1": "baseline_eims_iritis_scleritis",
            "baseline_eims_subother___8": "baseline_eims_sacroileitis",
            "baseline_eims_subother___11": "baseline_eims_conjunctivitis",
            "baseline_eims_subother___14": "baseline_eims_angular_cheilitis",
            "baseline_eims_subother___99": "baseline_eims_other",
            "baseline_eims_other": "baseline_eims_other_text",
            "mh_appendix1": "previous_appendicectomy",
            "mh_tonsilout1": "previous_tonsillectomy",
            "eims_psc": "baseline_eims_psc",
            "mh_appendicetomy_age": "appendicectomy_age",
            "mh_tonsilectomy_age": "tonsillectomy_age",
            "mh_diagnosis_1": "pmh_1_diagnosis",
            "active_diagnosis1": "pmh_1_active",
            "mh_diagnosis_2": "pmh_2_diagnosis",
            "active_diagnosis2": "pmh_2_active",
            "mh_diagnosis_3": "pmh_3_diagnosis",
            "active_diagnosis3": "pmh_3_active",
            "mh_diagnosis_4": "pmh_4_diagnosis",
            "active_diagnosis4": "pmh_4_active",
            "mh_diagnosis_5": "pmh_5_diagnosis",
            "active_diagnosis5": "pmh_5_active",
            "mh_diagnosis_6": "pmh_6_diagnosis",
            "active_diagnosis6": "pmh_6_active",
            "mh_diagnosis_7": "pmh_7_diagnosis",
            "active_diagnosis7": "pmh_7_active",
            "mh_comments": "pmh_comments",
            "fh_total_siblings": "fh_number_siblings",
            "family_history_ibd": "fh_of_ibd_present",
            "number_fh_ibd": "fh_of_ibd_number_affected",
            "relationship_fh_ibd": "fh_1_relationship",
            "fh_age_at_diagnosis": "fh_1_age_at_diagnosis",
            "family_diagnosis_1": "fh_1_diagnosis",
            "family_diagnosis_other1": "fh_1_diagnosis_other",
            "fh_other_immune_condition1": "fh_1_diagnosis_other_text",
            "relationship_fh_ibd_2": "fh_2_relationship",
            "fh_age_at_diagnosis_2": "fh_2_age_at_diagnosis",
            "family_diagnosis_2": "fh_2_diagnosis",
            "family_diagnosis_other2": "fh_2_diagnosis_other",
            "fh_other_immune_condition2": "fh_2_diagnosis_other_text",
            "relationship_fh_ibd_3": "fh_3_relationship",
            "fh_age_at_diagnosis_3": "fh_3_age_at_diagnosis",
            "family_diagnosis_3": "fh_3_diagnosis",
            "family_diagnosis_other3": "fh_3_diagnosis_other",
            "fh_other_immune_condition3": "fh_3_diagnosis_other_text",
            "relationship_fh_ibd_4": "fh_4_relationship",
            "fh_age_at_diagnosis_4": "fh_4_age_at_diagnosis",
            "family_diagnosis_4": "fh_4_diagnosis",
            "family_diagnosis_other4": "fh_4_diagnosis_other",
            "fh_other_immune_condition4": "fh_4_diagnosis_other_text",
            "relationship_fh_ibd_5": "fh_5_relationship",
            "fh_age_at_diagnosis_5": "fh_5_age_at_diagnosis",
            "family_diagnosis_5": "fh_5_diagnosis",
            "family_diagnosis_other5": "fh_5_diagnosis_other",
            "fh_other_immune_condition5": "fh_5_diagnosis_other_text",
            "fh_patdetailscomments": "fh_comments",
            "gender": "sex",
            "ibd_diagnosis_category": "study_group",
            "incident_case": "new_diagnosis_of_ibd",
            "fatigue_score": "promis_fatigue_score",
            "study_site": "study_center",
            "patient_age_diagnosis": "age_at_diagnosis",
            "pucaiscore": "pucai_score",
            "pcdaiscore": "pcdai_score",
            "pcdai_freq": "pcdai_frequency",
            "type_eim___1": "pcdai_eim_fever",
            "type_eim___2": "pcdai_eim_arthritis",
            "type_eim___3": "pcdai_eim_uveitis",
            "type_eim___4": "pcdai_eim_erythema_nodosum",
            "type_eim___5": "pcdai_eim_pyoderma",
            "type_eim___6": "pcdai_eim_other",
            "other_eim": "pcdai_eim_other_text",
            "cdparis_ugidisease": "cdparis_upper_gi",
            "een_useyn": "een_use",
            "other_formula": "een_formula_type_text",
            "een_startdate": "een_start_date",
            "een_enddate": "een_end_date",
            "still_taken_een": "een_still_taken",
            "ucpariscomments": "ucparis_comments",
            "patient_active_symptomyn": "has_active_symptoms",
            "pgassessment": "physician_global_assessment",
            "baseline_symptoms_desc2___1": "symptoms_abdominal_pain",
            "baseline_symptoms_desc2___2": "symptoms_diarrhoea",
            "baseline_symptoms_desc2___3": "symptoms_urgency",
            "baseline_symptoms_desc2___4": "symptoms_pr_bleeding",
            "baseline_symptoms_desc2___5": "symptoms_weight_loss",
            "baseline_symptoms_desc2___6": "symptoms_fatigue",
            "baseline_symptoms_desc2___7": "symptoms_perianal",
            "other_symptoms": "symptoms_other_text",
            "paris_changeyn": "paris_change",
            "activityassesscomments": "disease_activity_score_comments",
            "endoscopy_type___2": "endoscopy_type_colonoscopy",
            "endoscopy_type___3": "endoscopy_type_upper_gi_endoscopy",
            "endoscopy_result": "endoscopy_report",
            "histopathology_report_text": "pathology_report",
            "uceis_total_score": "uceis_calc",
            "sescd_total_score": "sescd_calc",
            "est_endoscopic_severity": "physician_endoscopic_severity",
            "ct_abdomen_and_or_pelvis": "ct_abdomen_pelvis",
            "abdominal_uss": "uss_abdomen",
            "abdominal_x_ray": "axr",
            "abdous_date": "uss_abdomen_date",
            "abdous_report": "uss_abdomen_report",
            "mrisb_date": "mri_small_bowel_date",
            "mrisb_report": "mri_small_bowel_report",
            "ibd_surgery_si": "ibd_surgery_performed",
            "surgery_date_si": "ibd_surgery_date",
            "ibd_procedure_type": "ibd_surgery_procedure",
            "ibd_procedure_type_other": "ibd_surgery_procedure_other",
            "ibd_other_specify_proc": "ibd_surgery_procedure_other_text",
            "ibd_procedure_result": "ibd_surgery_comments",
            "histologycomments_si": "ibd_surgery_histology_report",
            "blood_test_date1": "nhs_bloods_date",
            "faecal_test_date_2": "calprotectin_date",
            "other_drug_level_assessed": "other_drug_level",
            "date_biologic_level": "drug_level_date",
            "drug_level_inflxi": "ifx_level",
            "drug_level_adalimumab": "ada_level",
            "drug_level_antibody_adali": "ada_antibody",
            "drug_level_antibody_inflx": "ifx_antibody",
            "patdetailscomments_as_lbt": "lab_tests_comments",
            "comment_if_any_of_these_qu": "proms_comments",
            "meds_summary___1": "sampling_asa",
            "meds_summary___2": "sampling_een",
            "meds_summary___13": "sampling_on_no_meds",
            "meds_summary___3": "sampling_steroids_oral",
            "meds_summary___4": "sampling_steroids_iv",
            "meds_summary___5": "sampling_steroids_topical",
            "meds_summary___6": "sampling_imm",
            "meds_summary___7": "sampling_mtx",
            "meds_summary___8": "sampling_ifx",
            "meds_summary___9": "sampling_ada",
            "meds_summary___10": "sampling_vedo",
            "meds_summary___11": "sampling_uste",
            "meds_summary___12": "sampling_other",
            "other_drug_summary": "sampling_other_text",
            "drug": "ibd_drug_1_name",
            "other_drug": "ibd_drug_1_name_other",
            "drug_dose": "ibd_drug_1_dose",
            "drug_frequency": "ibd_drug_1_frequency",
            "drug_other_frequency": "ibd_drug_1_frequency_other",
            "drug_start_date": "ibd_drug_1_start_date",
            "still_taken_drug0": "ibd_drug_1_still_taking",
            "drug_end_date": "ibd_drug_1_end_date",
            "reason_stop_drug_0": "ibd_drug_1_reason_stopped",
            "bpt_other_reason_0": "ibd_drug_1_reason_stopped_text",
            "drug_1": "ibd_drug_2_name",
            "other_drug_1": "ibd_drug_2_name_other",
            "drug_dose_1": "ibd_drug_2_dose",
            "currently_frequency_use_1": "ibd_drug_2_frequency",
            "drug_other_frequency_1": "ibd_drug_2_frequency_other",
            "drug_startdate1": "ibd_drug_2_start_date",
            "still_taken_drug1": "ibd_drug_2_still_taking",
            "other_drug_enddate": "ibd_drug_2_end_date",
            "reason_stop_drug_1": "ibd_drug_2_reason_stopped",
            "bpt_other_reason_1": "ibd_drug_2_reason_stopped_text",
            "drug_2": "ibd_drug_3_name",
            "other_drug_2": "ibd_drug_3_name_other",
            "drug_dose_2": "ibd_drug_3_dose",
            "currently_frequency_use_2": "ibd_drug_3_frequency",
            "drug_other_frequency_2": "ibd_drug_3_frequency_other",
            "drug_startdate_2": "ibd_drug_3_start_date",
            "still_taken_drug2": "ibd_drug_3_still_taking",
            "drug_enddate_2": "ibd_drug_3_end_date",
            "reason_stop_drug_2": "ibd_drug_3_reason_stopped",
            "bpt_other_reason_2": "ibd_drug_3_reason_stopped_text",
            "drug_3": "ibd_drug_4_name",
            "other_drug_3": "ibd_drug_4_name_other",
            "drug_dose_3": "ibd_drug_4_dose",
            "currently_frequency_use_3": "ibd_drug_4_frequency",
            "drug_other_frequency_3": "ibd_drug_4_frequency_other",
            "drug_startdate_3": "ibd_drug_4_start_date",
            "still_taken_drug3": "ibd_drug_4_still_taking",
            "drug_enddate_3": "ibd_drug_4_end_date",
            "reason_stop_drug_3": "ibd_drug_4_reason_stopped",
            "bpt_other_reason_3": "ibd_drug_4_reason_stopped_text",
            "drug_4": "ibd_drug_5_name",
            "other_drug_4": "ibd_drug_5_name_other",
            "drug_dose_4": "ibd_drug_5_dose",
            "currently_frequency_use_4": "ibd_drug_5_frequency",
            "drug_other_frequency_4": "ibd_drug_5_frequency_other",
            "drug_startdate_4": "ibd_drug_5_start_date",
            "still_taken_drug4": "ibd_drug_5_still_taking",
            "drug_enddate_4": "ibd_drug_5_end_date",
            "reason_stop_drug_4": "ibd_drug_5_reason_stopped",
            "bpt_other_reason_4": "ibd_drug_5_reason_stopped_text",
            "non_ibddrugyn": "concomitant_non_ibd_drug",
            "conc_drug_cm1": "concomitant_drug_1_name",
            "concomit_other_drug_cm1": "concomitant_drug_1_name_other",
            "dt_conc_dose": "concomitant_drug_1_dose",
            "conc_frequency1": "concomitant_drug_1_frequency",
            "conc_frequencyother1": "concomitant_drug_1_frequency_other",
            "conc_drug_cm2": "concomitant_drug_2_name",
            "concomit_other_drug_cm2": "concomitant_drug_2_name_other",
            "dt_conc_dose_2": "concomitant_drug_2_dose",
            "conc_frequency2": "concomitant_drug_2_frequency",
            "conc_frequencyother2": "concomitant_drug_2_frequency_other",
            "conc_drug_cm3": "concomitant_drug_3_name",
            "concomit_other_drug_cm3": "concomitant_drug_3_name_other",
            "dt_conc_dose_3": "concomitant_drug_3_dose",
            "conc_frequency3": "concomitant_drug_3_frequency",
            "conc_frequencyother3": "concomitant_drug_3_frequency_other",
            "conc_drug_cm4": "concomitant_drug_4_name",
            "concomit_other_drug_cm4": "concomitant_drug_4_name_other",
            "dt_conc_dose_4": "concomitant_drug_4_dose",
            "conc_frequency4": "concomitant_drug_4_frequency",
            "conc_frequencyother4": "concomitant_drug_4_frequency_other",
            "conc_drug_cm5": "concomitant_drug_5_name",
            "concomit_other_drug_cm5": "concomitant_drug_5_name_other",
            "dt_conc_dose_5": "concomitant_drug_5_dose",
            "conc_frequency5": "concomitant_drug_5_frequency",
            "conc_frequencyother5": "concomitant_drug_5_frequency_other",
            "drug_comments_prvcm": "current_drugs_comments",
            "baseline_current_drug": "baseline_ibd_drug_1",
            "baseline_current_other1": "baseline_ibd_drug_1_other",
            "baseline_current_otherx1": "baseline_ibd_drug_1_other_text",
            "baseline_current_ibd_dose1": "baseline_ibd_drug_1_dose",
            "bl_current_frequency_use1": "baseline_ibd_drug_1_frequency",
            "bl_prev_frequency_other1": "baseline_ibd_drug_1_frequency_other",
            "baseline_start_date_ibd1": "baseline_ibd_drug_1_start_date",
            "baseline_end_date1": "baseline_ibd_drug_1_end_date",
            "baseline_drug_stop1": "baseline_ibd_drug_1_reason_stopped",
            "baseline_other_reason1": "baseline_ibd_drug_1_reason_stopped_text",
            "baseline_current_drug_2": "baseline_ibd_drug_2",
            "baseline_current_other2": "baseline_ibd_drug_2_other",
            "baseline_current_otherx2": "baseline_ibd_drug_2_other_text",
            "baseline_current_ibd_dose2": "baseline_ibd_drug_2_dose",
            "bl_current_frequency_use2": "baseline_ibd_drug_2_frequency",
            "bl_prev_frequency_other2": "baseline_ibd_drug_2_frequency_other",
            "baseline_start_date_ibd2": "baseline_ibd_drug_2_start_date",
            "baseline_end_date2": "baseline_ibd_drug_2_end_date",
            "baseline_drug_stop2": "baseline_ibd_drug_2_reason_stopped",
            "baseline_other_reason2": "baseline_ibd_drug_2_reason_stopped_text",
            "baseline_current_drug_3": "baseline_ibd_drug_3",
            "baseline_current_other3": "baseline_ibd_drug_3_other",
            "baseline_current_otherx3": "baseline_ibd_drug_3_other_text",
            "baseline_current_ibd_dose3": "baseline_ibd_drug_3_dose",
            "bl_current_frequency_use3": "baseline_ibd_drug_3_frequency",
            "bl_prev_frequency_other3": "baseline_ibd_drug_3_frequency_other",
            "baseline_start_date_ibd3": "baseline_ibd_drug_3_start_date",
            "baseline_end_date3": "baseline_ibd_drug_3_end_date",
            "baseline_drug_stop3": "baseline_ibd_drug_3_reason_stopped",
            "baseline_other_reason3": "baseline_ibd_drug_3_reason_stopped_text",
            "baseline_current_drug_4": "baseline_ibd_drug_4",
            "baseline_current_other4": "baseline_ibd_drug_4_other",
            "baseline_current_otherx4": "baseline_ibd_drug_4_other_text",
            "baseline_current_ibd_dose4": "baseline_ibd_drug_4_dose",
            "bl_current_frequency_use4": "baseline_ibd_drug_4_frequency",
            "bl_prev_frequency_other4": "baseline_ibd_drug_4_frequency_other",
            "baseline_start_date_ibd4": "baseline_ibd_drug_4_start_date",
            "baseline_end_date4": "baseline_ibd_drug_4_end_date",
            "baseline_drug_stop4": "baseline_ibd_drug_4_reason_stopped",
            "baseline_other_reason4": "baseline_ibd_drug_4_reason_stopped_text",
            "baseline_current_drug_5": "baseline_ibd_drug_5",
            "baseline_current_other5": "baseline_ibd_drug_5_other",
            "baseline_current_otherx5": "baseline_ibd_drug_5_other_text",
            "baseline_current_ibd_dose5": "baseline_ibd_drug_5_dose",
            "bl_current_frequency_use5": "baseline_ibd_drug_5_frequency",
            "bl_prev_frequency_other5": "baseline_ibd_drug_5_frequency_other",
            "baseline_start_date_ibd5": "baseline_ibd_drug_5_start_date",
            "baseline_end_date5": "baseline_ibd_drug_5_end_date",
            "baseline_drug_stop5": "baseline_ibd_drug_5_reason_stopped",
            "baseline_other_reason5": "baseline_ibd_drug_5_reason_stopped_text",
        },
        inplace=True,
    )

    # Drug Mapping
    baseline_ibd_drug_map = {
        "21": "asa",
        "1": "ada",
        "2": "aza",
        "16": "mp",
        "3": "ifx",
        "11": "uste",
        "12": "vedo",
        "15": "goli",
        "10": "tofa",
        "13": "een",
        "99": "other",
    }

    df["baseline_ibd_drug_1"] = df["baseline_ibd_drug_1"].map(baseline_ibd_drug_map)
    df["baseline_ibd_drug_2"] = df["baseline_ibd_drug_2"].map(baseline_ibd_drug_map)
    df["baseline_ibd_drug_3"] = df["baseline_ibd_drug_3"].map(baseline_ibd_drug_map)
    df["baseline_ibd_drug_4"] = df["baseline_ibd_drug_4"].map(baseline_ibd_drug_map)
    df["baseline_ibd_drug_5"] = df["baseline_ibd_drug_5"].map(baseline_ibd_drug_map)

    baseline_ibd_other_drug_map = {
        "14": "mtx",
        "8": "steroid_enema",
        "9": "steroid_suppositories",
        "4": "mesalazine_enema",
        "5": "asa",
        "6": "mesalazine_suppositories",
        "19": "methylprednisolone",
        "7": "prednisolone",
        "13": "budesonide",
        "99": "other",
    }

    df["baseline_ibd_drug_1_other"] = df["baseline_ibd_drug_1_other"].map(
        baseline_ibd_other_drug_map
    )
    df["baseline_ibd_drug_2_other"] = df["baseline_ibd_drug_2_other"].map(
        baseline_ibd_other_drug_map
    )
    df["baseline_ibd_drug_3_other"] = df["baseline_ibd_drug_3_other"].map(
        baseline_ibd_other_drug_map
    )
    df["baseline_ibd_drug_4_other"] = df["baseline_ibd_drug_4_other"].map(
        baseline_ibd_other_drug_map
    )
    df["baseline_ibd_drug_5_other"] = df["baseline_ibd_drug_5_other"].map(
        baseline_ibd_other_drug_map
    )

    ibd_drug_map = {
        "1": "ada",
        "2": "aza",
        "57": "een",
        "16": "mp",
        "14": "mtx",
        "3": "ifx",
        "11": "uste",
        "12": "vedo",
        "15": "goli",
        "10": "tofa",
        "17": "filgo",
        "18": "upa",
        "8": "steroid_enema",
        "9": "steroid_suppositories",
        "4": "mesalazine_enema",
        "5": "asa",
        "6": "mesalazine_suppositories",
        "19": "methylprednisolone",
        "7": "prednisolone",
        "13": "budesonide",
        "99": "other",
    }

    df["ibd_drug_1_name"] = df["ibd_drug_1_name"].map(ibd_drug_map)
    df["ibd_drug_2_name"] = df["ibd_drug_2_name"].map(ibd_drug_map)
    df["ibd_drug_3_name"] = df["ibd_drug_3_name"].map(ibd_drug_map)
    df["ibd_drug_4_name"] = df["ibd_drug_4_name"].map(ibd_drug_map)
    df["ibd_drug_5_name"] = df["ibd_drug_5_name"].map(ibd_drug_map)

    concomitant_drug_map = {
        "1": "opiates",
        "2": "antibiotics",
        "3": "proton_pump_inhibitors",
        "4": "non_steroidals",
        "99": "other",
    }

    df["concomitant_drug_1_name"] = df["concomitant_drug_1_name"].map(
        concomitant_drug_map
    )
    df["concomitant_drug_2_name"] = df["concomitant_drug_2_name"].map(
        concomitant_drug_map
    )
    df["concomitant_drug_3_name"] = df["concomitant_drug_3_name"].map(
        concomitant_drug_map
    )
    df["concomitant_drug_4_name"] = df["concomitant_drug_4_name"].map(
        concomitant_drug_map
    )
    df["concomitant_drug_5_name"] = df["concomitant_drug_5_name"].map(
        concomitant_drug_map
    )

    drug_frequency_map = {
        "1": "od",
        "2": "bd",
        "3": "tds",
        "4": "qds",
        "5": "once_a_week",
        "6": "fortnightly",
        "7": "monthly",
        "8": "six_weekly",
        "9": "eight_weekly",
        "10": "three_monthly",
        "11": "prn",
        "12": "alternate_days",
        "13": "six_times_a_day",
        "14": "five_times_a_day",
        "99": "other",
    }

    df["ibd_drug_1_frequency"] = df["ibd_drug_1_frequency"].map(drug_frequency_map)
    df["ibd_drug_2_frequency"] = df["ibd_drug_2_frequency"].map(drug_frequency_map)
    df["ibd_drug_3_frequency"] = df["ibd_drug_3_frequency"].map(drug_frequency_map)
    df["ibd_drug_4_frequency"] = df["ibd_drug_4_frequency"].map(drug_frequency_map)
    df["ibd_drug_5_frequency"] = df["ibd_drug_5_frequency"].map(drug_frequency_map)
    df["concomitant_drug_1_frequency"] = df["concomitant_drug_1_frequency"].map(
        drug_frequency_map
    )
    df["concomitant_drug_2_frequency"] = df["concomitant_drug_2_frequency"].map(
        drug_frequency_map
    )
    df["concomitant_drug_3_frequency"] = df["concomitant_drug_3_frequency"].map(
        drug_frequency_map
    )
    df["concomitant_drug_4_frequency"] = df["concomitant_drug_4_frequency"].map(
        drug_frequency_map
    )
    df["concomitant_drug_5_frequency"] = df["concomitant_drug_5_frequency"].map(
        drug_frequency_map
    )
    df["baseline_ibd_drug_1_frequency"] = df["baseline_ibd_drug_1_frequency"].map(
        drug_frequency_map
    )
    df["baseline_ibd_drug_2_frequency"] = df["baseline_ibd_drug_2_frequency"].map(
        drug_frequency_map
    )
    df["baseline_ibd_drug_3_frequency"] = df["baseline_ibd_drug_3_frequency"].map(
        drug_frequency_map
    )
    df["baseline_ibd_drug_4_frequency"] = df["baseline_ibd_drug_4_frequency"].map(
        drug_frequency_map
    )
    df["baseline_ibd_drug_5_frequency"] = df["baseline_ibd_drug_5_frequency"].map(
        drug_frequency_map
    )

    reason_stopped_map = {
        "1": "primary_non_response",
        "2": "secondary_non_response",
        "3": "treatment_completed",
        "9": "intolerance",
        "7": "adverse_effects",
        "10": "confirmed_immunogenicity",
        "99": "other",
    }

    df["ibd_drug_1_reason_stopped"] = df["ibd_drug_1_reason_stopped"].map(
        reason_stopped_map
    )
    df["ibd_drug_2_reason_stopped"] = df["ibd_drug_2_reason_stopped"].map(
        reason_stopped_map
    )
    df["ibd_drug_3_reason_stopped"] = df["ibd_drug_3_reason_stopped"].map(
        reason_stopped_map
    )
    df["ibd_drug_4_reason_stopped"] = df["ibd_drug_4_reason_stopped"].map(
        reason_stopped_map
    )
    df["ibd_drug_5_reason_stopped"] = df["ibd_drug_5_reason_stopped"].map(
        reason_stopped_map
    )
    df["baseline_ibd_drug_1_reason_stopped"] = df[
        "baseline_ibd_drug_1_reason_stopped"
    ].map(reason_stopped_map)
    df["baseline_ibd_drug_2_reason_stopped"] = df[
        "baseline_ibd_drug_2_reason_stopped"
    ].map(reason_stopped_map)
    df["baseline_ibd_drug_3_reason_stopped"] = df[
        "baseline_ibd_drug_3_reason_stopped"
    ].map(reason_stopped_map)
    df["baseline_ibd_drug_4_reason_stopped"] = df[
        "baseline_ibd_drug_4_reason_stopped"
    ].map(reason_stopped_map)
    df["baseline_ibd_drug_5_reason_stopped"] = df[
        "baseline_ibd_drug_5_reason_stopped"
    ].map(reason_stopped_map)

    df["fh_of_ibd_present"] = df["fh_of_ibd_present"].map(
        {"1": "yes", "2": "no", "3": "unclear"}
    )

    fh_diagnosis_map = {
        "6": "cd",
        "7": "uc",
        "9": "ibdu",
        "10": "possible_cd",
        "11": "possible_uc",
        "12": "possible_ibd",
        "99": "other",
    }

    fh_diagnosis_other_map = {
        "1": "multiple_sclerosis",
        "2": "psoriasis",
        "3": "coeliac_disease",
        "4": "ankylosing_spondylitis",
        "5": "colorectal_cancer",
        "8": "ibs",
        "13": "any_cancer",
        "99": "other",
    }

    fh_relationship_map = {
        "1": "parent",
        "27": "mother",
        "28": "father",
        "2": "sibling",
        "3": "sister",
        "4": "brother",
        "5": "cousin",
        "6": "uncle",
        "7": "aunt",
        "8": "uncle_maternal",
        "9": "aunt_maternal",
        "10": "uncle_paternal",
        "11": "aunt_paternal",
        "29": "grandparent",
        "12": "grandmother_paternal",
        "24": "grandmother_maternal",
        "25": "grandfather_paternal",
        "26": "grandfather_maternal",
        "30": "granduncle_paternal",
        "31": "granduncle_maternal",
        "13": "half_brother",
        "14": "half_sister",
        "15": "nephew",
        "16": "niece",
        "17": "grandson",
        "18": "granddaughter",
        "19": "other_2nd_degree",
        "20": "other_3rd_degree",
        "21": "other_4th_degree",
        "22": "dizygotic_twin",
        "23": "monozygotic_twin",
    }

    df["fh_1_diagnosis"] = df["fh_1_diagnosis"].map(fh_diagnosis_map)
    df["fh_2_diagnosis"] = df["fh_2_diagnosis"].map(fh_diagnosis_map)
    df["fh_3_diagnosis"] = df["fh_3_diagnosis"].map(fh_diagnosis_map)
    df["fh_4_diagnosis"] = df["fh_4_diagnosis"].map(fh_diagnosis_map)
    df["fh_5_diagnosis"] = df["fh_5_diagnosis"].map(fh_diagnosis_map)

    df["fh_1_diagnosis_other"] = df["fh_1_diagnosis_other"].map(fh_diagnosis_other_map)
    df["fh_2_diagnosis_other"] = df["fh_2_diagnosis_other"].map(fh_diagnosis_other_map)
    df["fh_3_diagnosis_other"] = df["fh_3_diagnosis_other"].map(fh_diagnosis_other_map)
    df["fh_4_diagnosis_other"] = df["fh_4_diagnosis_other"].map(fh_diagnosis_other_map)
    df["fh_5_diagnosis_other"] = df["fh_5_diagnosis_other"].map(fh_diagnosis_other_map)

    df["fh_1_relationship"] = df["fh_1_relationship"].map(fh_relationship_map)
    df["fh_2_relationship"] = df["fh_2_relationship"].map(fh_relationship_map)
    df["fh_3_relationship"] = df["fh_3_relationship"].map(fh_relationship_map)
    df["fh_4_relationship"] = df["fh_4_relationship"].map(fh_relationship_map)
    df["fh_5_relationship"] = df["fh_5_relationship"].map(fh_relationship_map)

    df["new_flare_up"] = df["new_flare_up"].map(
        {
            "0": "no",
            "1": "yes",
            "3": "ongoing_from_previous_visit",
        }
    )
    df["flare_up_1_setting"] = df["flare_up_1_setting"].map(
        {"1": "outpatient", "2": "inpatient"}
    )
    df["flare_up_2_setting"] = df["flare_up_2_setting"].map(
        {"1": "outpatient", "2": "inpatient"}
    )
    df["steroid_use_1_reason"] = df["steroid_use_1_reason"].map(
        {"1": "flare_up", "99": "other"}
    )
    df["steroid_use_2_reason"] = df["steroid_use_2_reason"].map(
        {"1": "flare_up", "99": "other"}
    )
    df["steroid_use_1_drug"] = df["steroid_use_1_drug"].map(
        {
            "8": "steroid_enema",
            "9": "steroid_suppositories",
            "7": "prednisolone",
            "13": "budesonide",
            "21": "budesonide",
            "20": "hydrocortisone",
            "19": "methylprednisolone",
            "99": "other",
        }
    )
    df["steroid_use_2_drug"] = df["steroid_use_2_drug"].map(
        {
            "8": "steroid_enema",
            "9": "steroid_suppositories",
            "7": "prednisolone",
            "13": "budesonide",
            "21": "budesonide",
            "20": "hydrocortisone",
            "19": "methylprednisolone",
            "99": "other",
        }
    )
    df["steroid_use_1_still_taking"] = df["steroid_use_1_still_taking"].map(
        {"1": "yes", "0": "no"}
    )
    df["steroid_use_2_still_taking"] = df["steroid_use_2_still_taking"].map(
        {"1": "yes", "0": "no"}
    )

    # this differs from music
    df["steroid_use_1_reason_stopped"] = df["steroid_use_1_reason_stopped"].map(
        {
            "1": "primary_non_response",
            "2": "successful_steroid_wean",
            "3": "change_in_preparation",
            "4": "intolerance",
            "5": "adverse_effects",
            "99": "other",
        }
    )
    df["steroid_use_2_reason_stopped"] = df["steroid_use_2_reason_stopped"].map(
        {
            "1": "primary_non_response",
            "2": "successful_steroid_wean",
            "3": "change_in_preparation",
            "4": "intolerance",
            "5": "adverse_effects",
            "99": "other",
        }
    )
    df["steroid_use_1_reason_changed"] = df["steroid_use_1_reason_changed"].map(
        {"1": "increased_for_symptom_control", "2": "planned_reduction", "99": "other"}
    )
    df["steroid_use_2_reason_changed"] = df["steroid_use_2_reason_changed"].map(
        {"1": "increased_for_symptom_control", "2": "planned_reduction", "99": "other"}
    )

    df["new_oral_steroids_since_last_visit"] = df[
        "new_oral_steroids_since_last_visit"
    ].map({"1": "yes", "0": "no", "3": "ongoing_since_last_visit"})

    df["has_active_symptoms"] = df["has_active_symptoms"].map({"1": "yes", "0": "no"})
    df["paris_change"] = df["paris_change"].map({"1": "yes", "0": "no"})
    df["symptoms_abdominal_pain"] = df["symptoms_abdominal_pain"].map(
        {"1": "yes", "0": "no"}
    )
    df["symptoms_diarrhoea"] = df["symptoms_diarrhoea"].map({"1": "yes", "0": "no"})
    df["symptoms_urgency"] = df["symptoms_urgency"].map({"1": "yes", "0": "no"})
    df["symptoms_pr_bleeding"] = df["symptoms_pr_bleeding"].map({"1": "yes", "0": "no"})
    df["symptoms_weight_loss"] = df["symptoms_weight_loss"].map({"1": "yes", "0": "no"})
    df["symptoms_fatigue"] = df["symptoms_fatigue"].map({"1": "yes", "0": "no"})
    df["symptoms_perianal"] = df["symptoms_perianal"].map({"1": "yes", "0": "no"})

    df["een_use"] = df["een_use"].map({"1": "yes", "0": "no"})

    df["een_formula_type"] = df["een_formula_type"].map(
        {
            "1": "modulen_ibd",
            "2": "fortisip",
            "3": "nutrison_energy",
            "4": "elemental_eo28",
            "5": "pediasure",
            "6": "nutrini",
            "7": "neocate_jr",
            "8": "other",
        }
    )
    df["een_still_taken"] = df["een_still_taken"].map(
        {
            "1": "yes",
            "0": "no",
        }
    )
    df["unplanned_hospital_admission"] = df["unplanned_hospital_admission"].map(
        {
            "0": "no",
            "1": "yes",
        }
    )
    df["new_diagnosis_of_ibd"] = df["new_diagnosis_of_ibd"].map({"1": "yes", "2": "no"})
    df["redcap_event_name"] = df["redcap_event_name"].map(
        {
            "timepoint_1_arm_1": "timepoint_1",
            "timepoint_2_arm_1": "timepoint_2",
            "timepoint_3_arm_1": "timepoint_3",
        }
    )
    df["sex"] = df["sex"].map(
        {
            "1": "male",
            "2": "female",
        }
    )
    df["study_group"] = df["study_group"].map(
        {
            "1": "cd",
            "2": "uc",
            "3": "ibdu",
            "4": "non_ibd",
        }
    )

    df["disease_activity"] = df["disease_activity"].map(
        {
            "1": "remission",
            "2": "mild",
            "3": "moderate",
            "4": "severe",
            "5": "not_applicable",
        }
    )

    df["physician_global_assessment"] = df["physician_global_assessment"].map(
        {
            "1": "biochem_remission",
            "2": "clinical_remission",
            "3": "mild",
            "4": "moderate",
            "5": "severe",
            "-1000": "not_applicable",
        }
    )

    df["study_center"] = df["study_center"].map(
        {"1": "edinburgh", "2": "glasgow", "3": "dundee", "4": "aberdeen", "5": "other"}
    )

    df["patient_age_group"] = df["patient_age_group"].map(
        {
            "0": "6-10",
            "1": "10-13",
            "2": "14-18",
            "99": "no_data",
        }
    )
    df["pucai_pain"] = df["pucai_pain"].map(
        {
            "0": "0",
            "1": "5",
            "2": "10",
        }
    )

    df["pucai_bleeding"] = df["pucai_bleeding"].map(
        {
            "0": "0",
            "1": "10",
            "2": "20",
            "3": "30",
        }
    )

    df["pucai_consistency"] = df["pucai_consistency"].map(
        {
            "1": "0",
            "2": "5",
            "3": "10",
        }
    )

    df["pucai_stools"] = df["pucai_stools"].map(
        {
            "1": "0",
            "2": "5",
            "3": "10",
            "4": "15",
        }
    )

    df["pucai_nocturnal"] = df["pucai_nocturnal"].map(
        {
            "1": "0",
            "2": "10",
        }
    )

    df["pucai_activity"] = df["pucai_activity"].map(
        {
            "1": "0",
            "2": "5",
            "3": "10",
        }
    )

    df["pcdai_pain"] = df["pcdai_pain"].map(
        {
            "1": "0",
            "2": "10",
            "3": "20",
        }
    )

    df["pcdai_general"] = df["pcdai_general"].map(
        {
            "1": "0",
            "2": "10",
            "3": "20",
        }
    )

    df["pcdai_frequency"] = df["pcdai_frequency"].map(
        {
            "1": "0",
            "2": "7.5",
            "3": "15",
        }
    )

    df["pcdai_esr"] = df["pcdai_esr"].map(
        {
            "1": "0",
            "2": "7.5",
            "3": "15",
        }
    )

    df["pcdai_alb"] = df["pcdai_alb"].map(
        {
            "1": "0",
            "2": "10",
            "3": "20",
        }
    )

    df["pcdai_weight"] = df["pcdai_weight"].map(
        {
            "1": "0",
            "2": "5",
            "3": "10",
        }
    )

    df["pcdai_perianal"] = df["pcdai_perianal"].map(
        {
            "1": "0",
            "2": "7.5",
            "3": "15",
        }
    )

    df["pcdai_eim"] = df["pcdai_eim"].map(
        {
            "1": "0",
            "2": "10",
        }
    )

    df["cdparis_upper_gi"] = df["cdparis_upper_gi"].map(
        {
            "1": "L4a",
            "2": "L4b",
            "3": "none",
        }
    )

    df["cdparis_behaviour"] = df["cdparis_behaviour"].map(
        {
            "0": "B1",
            "1": "B2",
            "2": "B3",
            "3": "B2+B3",
        }
    )

    df["cdparis_location"] = df["cdparis_location"].map(
        {
            "1": "L1",
            "2": "L2",
            "3": "L3",
            "4": "L4",
        }
    )

    df["cdparis_growth"] = df["cdparis_growth"].map(
        {
            "0": "G0",
            "1": "G1",
        }
    )

    df["cdparis_perianal"] = df["cdparis_perianal"].map({"1": "yes", "0": "no"})

    df["ucparis_severity"] = df["ucparis_severity"].map(
        {
            "0": "S0",
            "1": "S1",
        }
    )

    df["ucparis_extent"] = df["ucparis_extent"].map(
        {
            "0": "E1",
            "1": "E2",
            "2": "E3",
            "3": "E4",
        }
    )

    df["physician_endoscopic_severity"] = df["physician_endoscopic_severity"].map(
        {
            "1": "normal",
            "2": "mild",
            "3": "moderate",
            "4": "severe",
        }
    )

    df.replace("", np.nan, inplace=True)  # Finds blanks and replace with NaN
    df.dropna(
        axis=1, how="all", inplace=True
    )  # Drop all columns where every value is empty
    df["study_id"] = df["study_id"].apply(lambda x: f"MINI-{x}")

    rows, columns = df.shape
    context.add_output_metadata(
        {
            "dagster/row_count": rows,
            "column_count": columns,
            "columns": df.columns.to_list(),
            "preview": MetadataValue.md(df.head(3).to_markdown()),
        }
    )

    return df

```
