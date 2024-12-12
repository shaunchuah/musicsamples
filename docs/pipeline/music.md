# MUSIC

```py title="assets/music.py"
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
    io_manager_key="io_manager",
    description="Fetches MUSIC data from IGMM RedCap Server, re-engineers baseline drug columns, and drops unused columns",
    group_name="music",
)
def music_raw_dataframe(context: AssetExecutionContext) -> pd.DataFrame:
    MUSIC_API_TOKEN = EnvVar("MUSIC_API_TOKEN").get_value()
    music_redcap_url = "https://ecrf.igmm.ed.ac.uk/api/"
    redcap_api_data = {
        "token": f"{MUSIC_API_TOKEN}",
        "content": "record",
        "action": "export",
        "format": "json",
        "type": "flat",
        "csvDelimiter": "",
        "forms[0]": "patient_details",
        "forms[1]": "diagnosis",
        "forms[2]": "phenotyping",
        "forms[3]": "timepoints",
        "forms[4]": "patient_reported_activity_cucq32",
        "forms[5]": "laboratory_tests_for_disease_activity",
        "forms[6]": "endoscopic_disease_activity",
        "forms[7]": "surgical_intervention",
        "forms[8]": "saliva_sample",
        "forms[9]": "cleaned_drug_data",
        "forms[10]": "radiologic_disease_activity",
        "rawOrLabel": "raw",
        "rawOrLabelHeaders": "raw",
        "exportCheckboxLabel": "false",
        "exportSurveyFields": "false",
        "exportDataAccessGroups": "false",
        "returnFormat": "json",
    }
    response = requests.post(music_redcap_url, data=redcap_api_data)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame.from_records(data)

    df["baseline_5asa"] = df.apply(
        lambda row: 1
        if "21"
        in [
            row["baseline_current_drug"],
            row["baseline_current_drug_2"],
            row["baseline_current_drug_3"],
            row["baseline_current_drug_4"],
            row["baseline_current_drug_5"],
            row["baseline_current_drug_6"],
        ]
        else (
            1
            if any(
                x in ["4", "5", "6"]
                for x in [
                    row["baseline_current_other1"],
                    row["baseline_current_other2"],
                    row["baseline_current_other3"],
                    row["baseline_current_other4"],
                    row["baseline_current_other5"],
                    row["baseline_current_other6"],
                ]
            )
            else 0
        ),
        axis=1,
    )

    df["baseline_mtx"] = df.apply(
        lambda row: 1
        if "14"
        in [
            row["baseline_current_other1"],
            row["baseline_current_other2"],
            row["baseline_current_other3"],
            row["baseline_current_other4"],
            row["baseline_current_other5"],
            row["baseline_current_other6"],
        ]
        else 0,
        axis=1,
    )

    df["baseline_ifx"] = df.apply(
        lambda row: 1
        if "3"
        in [
            row["baseline_current_drug"],
            row["baseline_current_drug_2"],
            row["baseline_current_drug_3"],
            row["baseline_current_drug_4"],
            row["baseline_current_drug_5"],
            row["baseline_current_drug_6"],
        ]
        else 0,
        axis=1,
    )

    df["baseline_ada"] = df.apply(
        lambda row: 1
        if "1"
        in [
            row["baseline_current_drug"],
            row["baseline_current_drug_2"],
            row["baseline_current_drug_3"],
            row["baseline_current_drug_4"],
            row["baseline_current_drug_5"],
            row["baseline_current_drug_6"],
        ]
        else 0,
        axis=1,
    )

    df["baseline_aza"] = df.apply(
        lambda row: 1
        if "2"
        in [
            row["baseline_current_drug"],
            row["baseline_current_drug_2"],
            row["baseline_current_drug_3"],
            row["baseline_current_drug_4"],
            row["baseline_current_drug_5"],
            row["baseline_current_drug_6"],
        ]
        else 0,
        axis=1,
    )

    df["baseline_mp"] = df.apply(
        lambda row: 1
        if "16"
        in [
            row["baseline_current_drug"],
            row["baseline_current_drug_2"],
            row["baseline_current_drug_3"],
            row["baseline_current_drug_4"],
            row["baseline_current_drug_5"],
            row["baseline_current_drug_6"],
        ]
        else 0,
        axis=1,
    )

    df["baseline_uste"] = df.apply(
        lambda row: 1
        if "11"
        in [
            row["baseline_current_drug"],
            row["baseline_current_drug_2"],
            row["baseline_current_drug_3"],
            row["baseline_current_drug_4"],
            row["baseline_current_drug_5"],
            row["baseline_current_drug_6"],
        ]
        else 0,
        axis=1,
    )

    df["baseline_vedo"] = df.apply(
        lambda row: 1
        if "12"
        in [
            row["baseline_current_drug"],
            row["baseline_current_drug_2"],
            row["baseline_current_drug_3"],
            row["baseline_current_drug_4"],
            row["baseline_current_drug_5"],
            row["baseline_current_drug_6"],
        ]
        else 0,
        axis=1,
    )

    df["baseline_goli"] = df.apply(
        lambda row: 1
        if "15"
        in [
            row["baseline_current_drug"],
            row["baseline_current_drug_2"],
            row["baseline_current_drug_3"],
            row["baseline_current_drug_4"],
            row["baseline_current_drug_5"],
            row["baseline_current_drug_6"],
        ]
        else 0,
        axis=1,
    )

    df["baseline_tofa"] = df.apply(
        lambda row: 1
        if "10"
        in [
            row["baseline_current_drug"],
            row["baseline_current_drug_2"],
            row["baseline_current_drug_3"],
            row["baseline_current_drug_4"],
            row["baseline_current_drug_5"],
            row["baseline_current_drug_6"],
        ]
        else 0,
        axis=1,
    )

    df["baseline_filgo"] = df.apply(
        lambda row: 1
        if "Filgotinib"
        in [
            row["baseline_current_otherx1"],
            row["baseline_current_otherx2"],
            row["baseline_current_otherx3"],
            row["baseline_current_otherx4"],
            row["baseline_current_otherx5"],
            row["baseline_current_otherx6"],
        ]
        else 0,
        axis=1,
    )

    df["baseline_risa"] = df.apply(
        lambda row: 1
        if "Risankisumab"
        in [
            row["baseline_current_otherx1"],
            row["baseline_current_otherx2"],
            row["baseline_current_otherx3"],
            row["baseline_current_otherx4"],
            row["baseline_current_otherx5"],
            row["baseline_current_otherx6"],
        ]
        else 0,
        axis=1,
    )

    df.drop(
        columns=[
            "study_group",
            "pt_recorded_patient_id",
            "consent_person_initial",
            "date_data_entry",
            "date_enrolledconsent",
            "consent_person_initial",
            "baseline_recruitment_type",
            "consent_per_initial_other",
            "consent_form_version",
            "pis_version",
            "chi_no",
            "initial",
            "dob",
            "patemail",
            "pat_tel_no",
            "patdetailscomments",
            "consent_yn",
            "fv_yn",
            "gp_yn",
            "patient_details_complete",
            "diagnosis_complete",
            "patientdetailsage_2",
            "patient_reported_activity_cucq32_complete",
            "hbicomplications____1000",
            "sccaicomplications____1000",
            "timepoints_complete",
            "unplanned_hospital_reason2____1000",
            "unplanned_hospital_reason1____1000",
            "flare_up_manaegment2____1000",
            "flare_up_manaegment1____1000",
            "laboratory_tests_for_disease_activity_complete",
            "other_drug_level_assessed",
            "otherdruglevel",
            "drug_level_antibody_other",
            "unit_bilirubin",
            "unit_potassium",
            "unit_sodium",
            "unit_creatinine",
            "unit_urea",
            "unit_egfr",
            "unit_plt",
            "unit_basophils",
            "unit_eosinophils",
            "unit_monocytes",
            "unit_lymphocytes",
            "unit_neutrophils",
            "unit_wcc",
            "unit_haematocrit",
            "unit_rcc",
            "unit_hb",
            "unit_qfit",
            "cleaned_drug_data_complete",
            "surgical_intervention_complete",
            "endoscopic_disease_activity_complete",
            "other_endoscopy_type____1000",
            "endoscopy_type____1000",
            "phenotyping_complete",
            "baseline_radiology_type_o____1000",
            "baseline_radiology_type____1000",
            "baseline_radiology_type_o___10",
            "other_endoscopy_type_2____1000",
            "endoscopy_type_2____1000",
            "baseline_eims_subother____1000",
            "baseline_eims____1000",
            "montrl_uct_sever_montrl",
            "visit1",
            "sescd_tot",  # this is the sescd score for the endoscopy done in previous 12 months prior to recruitment. Only 3 patients have it recorded.
            "baseline_eims___99",
            "baseline_endoscopy",
            "baseline_radiology",
            "baseline_histologyresult",
            "baseline_ibd_date_1",
            "baseline_record_date_8",
            "baseline_ibd_drug_entry",
            "baseline_current_drug",
            "baseline_current_other1",
            "baseline_current_ibd_dose1",
            "bl_current_frequency_use1",
            "bl_prev_frequency_other1",
            "baseline_start_date_ibd1",
            "baseline_end_date1",
            "baseline_drug_stop1",
            "baseline_other_reason1",
            "baseline_current_drug_2",
            "baseline_current_other2",
            "baseline_current_ibd_dose2",
            "bl_current_frequency_use2",
            "bl_prev_frequency_other2",
            "baseline_start_date_ibd2",
            "baseline_end_date2",
            "baseline_drug_stop2",
            "baseline_other_reason2",
            "baseline_current_drug_3",
            "baseline_current_other3",
            "baseline_current_ibd_dose3",
            "bl_current_frequency_use3",
            "bl_prev_frequency_other3",
            "baseline_start_date_ibd3",
            "baseline_end_date3",
            "baseline_drug_stop3",
            "baseline_other_reason3",
            "baseline_current_drug_4",
            "baseline_current_other4",
            "baseline_current_ibd_dose4",
            "bl_current_frequency_use4",
            "bl_prev_frequency_other4",
            "baseline_start_date_ibd4",
            "baseline_end_date4",
            "baseline_drug_stop4",
            "baseline_other_reason4",
            "baseline_current_drug_5",
            "baseline_current_other5",
            "baseline_current_ibd_dose5",
            "bl_current_frequency_use5",
            "bl_prev_frequency_other5",
            "baseline_start_date_ibd5",
            "baseline_end_date5",
            "baseline_drug_stop5",
            "baseline_other_reason5",
            "baseline_current_drug_6",
            "baseline_current_other6",
            "baseline_current_ibd_dose6",
            "bl_current_frequency_use6",
            "bl_prev_frequency_other6",
            "baseline_start_date_ibd6",
            "baseline_end_date6",
            "baseline_drug_stop6",
            "baseline_other_reason6",
            "baseline_current_otherx1",
            "baseline_current_otherx2",
            "baseline_current_otherx3",
            "baseline_current_otherx4",
            "baseline_current_otherx5",
            "baseline_current_otherx6",
            "endoscopy_type_2___1",
            "other_endoscopy_type_2___4",
            "other_endoscopy_type_2___5",
            "other_endoscopy_type_2___6",
            "baseline_radiology_type___11",
            "baseline_radiology_type_o___1",
            "baseline_radiology_type_o___2",
            "baseline_radiology_type_o___4",
            "baseline_radiology_type_o___5",
            "baseline_radiology_type_o___8",
            "baseline_radiology_type_o___9",
            "baseline_radiology_type_o___10",
            "endoscopy_yn",
            "endoscopy_date_2",
            "endoscopy_type___1",
            "other_endoscopy_type___4",
            "other_endoscopy_type___5",
            "other_endoscopy_type___6",
            "uceisvascular_pattern",
            "uceisbleeding",
            "uceiserosions_and_ulcers",
            "ileum_explored_ses",
            "sesileumulcers",
            "sesnarrowings",
            "sessurfacevas",
            "sessurfaceucvas",
            "sescd_ileum_expl_score",
            "ses_right_colon_explored",
            "ses_caecum_ulcers",
            "ses_caecum_narrowings",
            "ses_caecum_vas",
            "ses_caecum_ucvas",
            "ses_caecum_endcos_score",
            "ses_transverse_colon",
            "ses_transverseulcers",
            "ses_transverse_narrowings",
            "ses_transverse_vas",
            "ses_transverse_ucvas",
            "sescd_transve_colon_score",
            "ses_left_colon_and_sigma",
            "ses_left_colon_sigma_uc",
            "ses_narrpowings_left_colon",
            "ses_narrowng_leftcolonvas",
            "ses_narrow_leftcolonucvas",
            "sescd_left_colon_score",
            "ses_rectum_explored",
            "ses_rectum_explored_ulcers",
            "ses_rectum_narrowing",
            "ses_rectum_vas",
            "ses_rectum_ucvas",
            "sescd_rectum_score",
            "adalimumab_test",
            "infliximab_test",
            "laboratory_rev_date",
            "blood_test_type",
            "faecal_testyn",
            "qfit_testyn",
            "eims_psc",
            "mh_any",
            "mh_num",
            "mh_1bsc",
            "mh_term_other1",
            "mh_2bsc",
            "mh_term_other2",
            "mh_3bsc",
            "mh_term_other3",
            "mh_4bsc",
            "mh_term_other4",
            "mh_5bsc",
            "mh_term_other5",
            "mh_6bsc",
            "mh_term_other6",
            "mh_7bsc",
            "mh_term_other7",
            "radiology_invest_rev_date",
            "radiology",
            "radiology_comments",
            "radiologic_disease_activity_complete",
            "surgical_invest_rev_date",
            "non_ibd_surgery",
        ],
        inplace=True,
    )

    df.replace("", np.nan, inplace=True)  # Finds blanks and replace with NaN
    df.dropna(
        axis=1, how="all", inplace=True
    )  # Drop all columns where every value is empty
    rows, columns = df.shape
    context.add_output_metadata(
        {
            "dagster/row_count": rows,
            "column_count": columns,
        }
    )
    return df


@asset(description="Stage 1 Cleaning - Reshape dataframe.", group_name="music")
def music_reshaped_dataframe(
    context: AssetExecutionContext, music_raw_dataframe: pd.DataFrame
) -> pd.DataFrame:
    df = music_raw_dataframe

    # Split the initial df into 3 components; 1 with lab tests, 1 with saliva samples and 1 with the rest
    intermediate_df = df[df["redcap_repeat_instrument"].isnull()].copy()
    lab_sampling_df = df[
        df["redcap_repeat_instrument"] == "laboratory_tests_for_disease_activity"
    ].copy()
    saliva_sampling_df = df[df["saliva_rev_date"].notnull()].copy()
    # we have to do this because some have redcap_repeat_instrument
    # but others don't have the repeat thing tagged onto the data.

    intermediate_df.dropna(axis=1, how="all", inplace=True)
    lab_sampling_df.dropna(axis=1, how="all", inplace=True)
    saliva_sampling_df.dropna(axis=1, how="all", inplace=True)

    # Remove the repeating instances. They don't add value.
    lab_sampling_df = lab_sampling_df[
        lab_sampling_df["redcap_repeat_instance"] == 1
    ]  # we lose only 1 row belonging to 92-1
    saliva_sampling_df = saliva_sampling_df[
        saliva_sampling_df["redcap_repeat_instance"] != 2
    ]  # we lose only 2 rows belonging to 90-55 and 90-92

    # Deduplicating columns
    lab_sampling_df.drop(
        columns=[
            "baseline_5asa",
            "baseline_aza",
            "baseline_mp",
            "baseline_uste",
            "baseline_vedo",
            "baseline_goli",
            "baseline_tofa",
            "baseline_filgo",
            "baseline_risa",
            "baseline_mtx",
            "baseline_ifx",
            "baseline_ada",
            "redcap_repeat_instance",
            "redcap_repeat_instrument",
        ],
        inplace=True,
    )

    saliva_columns = [
        "study_id",
        "redcap_event_name",
        "saliva_rev_date",
        "saliva_sample",
        "saliva_setting",
        "sample_date",
        "saliva_eim",
        "eims_details",
        "saliva_abx",
        "abx_detail",
        "saliva_abx3m",
        "abx3m_detail",
        "saliva_piercing",
        "saliva_brushing",
        "saliva_brush_tongue",
        "saliva_dietibd",
        "diet_details",
        "saliva_cs",
        "saliva_denture",
        "dentures_details",
        "comments_saliva",
    ]

    saliva_sampling_df = saliva_sampling_df[saliva_columns]

    # First merger of lab_sampling_df into the main df
    df = pd.merge(
        intermediate_df,
        lab_sampling_df,
        how="left",
        on=["study_id", "redcap_event_name"],
    )

    saliva_columns_to_remove = [
        "saliva_rev_date",
        "saliva_sample",
        "saliva_setting",
        "sample_date",
        "saliva_eim",
        "eims_details",
        "saliva_abx",
        "abx_detail",
        "saliva_abx3m",
        "abx3m_detail",
        "saliva_piercing",
        "saliva_brushing",
        "saliva_brush_tongue",
        "saliva_dietibd",
        "diet_details",
        "saliva_cs",
        "saliva_denture",
        "dentures_details",
        "comments_saliva",
    ]

    df.drop(columns=saliva_columns_to_remove, inplace=True)

    # Second stage merger of saliva sampling df into the main df
    df = pd.merge(
        df, saliva_sampling_df, how="left", on=["study_id", "redcap_event_name"]
    )

    # Take out withdrawn participants at point of withdrawal.
    df = df[df["withdrawn"] != "0"]  # surprisingly withdrawn is coded as 0 for yes
    df.drop(columns=["withdrawn"], inplace=True)

    rows, columns = df.shape
    context.add_output_metadata(
        {
            "dagster/row_count": rows,
            "column_count": columns,
        }
    )

    return df


@asset(
    description="Stage 2 Cleaning - Fixing all column and cell values",
    group_name="music",
)
def music_cleaned_dataframe(
    context: AssetExecutionContext, music_reshaped_dataframe: pd.DataFrame
) -> pd.DataFrame:
    df = music_reshaped_dataframe

    df.rename(
        columns={
            "montrlcdlocation_montrl": "montreal_cd_location",
            "montrlcdbehav_montrl": "montreal_cd_behaviour",
            "montrlucextent_montrl": "montreal_uc_extent",
            "montrl_uc_server": "montreal_uc_severity",
            "patientdetailsage": "age",
            "smokeryn": "smoking_status",
            "smokingex": "when_smoking_stopped",
            "ex_unit": "when_smoking_stopped_units",
            "patient_diagnose_age": "age_at_diagnosis",
            "bmi_height": "height",
            "bmi_weight": "weight",
            "patient_active_symptomyn": "has_active_symptoms",
            "clinician_perform_stat": "physician_global_assessment",
            "total_cucq32_scored": "cucq_total",
            "mayo_total_score": "mayo_total",
            "sccai_total_calculation": "sccai_total",
            "hbi_total_calculation": "hbi_total",
            "diagcartecomment": "diagnosis_comments",
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
            "cucq32q1": "cucq_1",
            "cucq32q2": "cucq_2",
            "cucq32q3": "cucq_3",
            "cucq32q4": "cucq_4",
            "cucq32q5": "cucq_5",
            "cucq32q6": "cucq_6",
            "cucq32q36": "cucq_7",
            "cucq32q8": "cucq_8",
            "cucq32q9": "cucq_9",
            "cucq32q35": "cucq_10",
            "cucq32q11": "cucq_11",
            "cucq32q12": "cucq_12",
            "cucq32q34": "cucq_13",
            "cucq32q37": "cucq_14",
            "cucq32q47": "cucq_15",
            "cucq32q16": "cucq_16",
            "cucq32q17": "cucq_17",
            "cucq32q18": "cucq_18",
            "cucq32q48": "cucq_19",
            "cucq32q20": "cucq_20",
            "cucq32q44": "cucq_21",
            "cucq32q22": "cucq_22",
            "cucq32q41": "cucq_23",
            "cucq32q38": "cucq_24",
            "cucq32q25": "cucq_25",
            "cucq32q39": "cucq_26",
            "cucq32q33": "cucq_27",
            "cucq32q42": "cucq_28",
            "cucq32q40": "cucq_29",
            "cucq32q43": "cucq_30",
            "cucq32q45": "cucq_31",
            "cucq32q46": "cucq_32",
            "cucq32_rev_date": "cucq_date",
            "comment_if_any_of_these_qu": "proms_comments",
            "sccaicomplications___0": "sccai_no_complications",
            "sccaicomplications___1": "sccai_arthralgia",
            "sccaicomplications___2": "sccai_uveitis",
            "sccaicomplications___3": "sccai_erythema_nodosum",
            "sccaicomplications___4": "sccai_pyoderma",
            "sccai_bowel_freqday": "sccai_bowel_frequency_day",
            "sccai_bowel_frequency_nigh": "sccai_bowel_frequency_night",
            "sccai_urgency_of_defecatio": "sccai_urgency",
            "hbicomplications___0": "hbi_no_complications",
            "hbicomplications___1": "hbi_arthralgia",
            "hbicomplications___2": "hbi_uveitis",
            "hbicomplications___3": "hbi_erythema_nodosum",
            "hbicomplications___4": "hbi_apthous_ulcers",
            "hbicomplications___5": "hbi_pyoderma",
            "hbicomplications___6": "hbi_anal_fissures",
            "hbicomplications___7": "hbi_new_fistula",
            "hbicomplications___8": "hbi_abscess",
            "hbiliquid_stools": "hbi_liquid_stools_present",
            "hbinumber_of_liquid_stools": "hbi_liquid_stools",
            "hbiabdominal_mass1": "hbi_abdominal_mass",
            "hbigeneral_well_being_as": "hbi_general_well_being",
            "hbiabdominal_pain": "hbi_abdominal_pain",
            "activityassesscomments": "disease_activity_score_comments",
            "da_rev_date": "disease_activity_score_date",
            "mayo_physician_global_asse": "mayo_physician_global_assessment",
            "visit_review_date": "visit_date",
            "baseline_symptoms_desc2": "symptoms_description",
            "patdetailscomments_as_lbt": "lab_tests_comments",
            "blood_test_date_red": "nhs_bloods_date",
            "endoscopy_result_endcospy": "endoscopy_report",
            "histopathology_report_text": "pathology_report",
            "flare_up_timeframe1": "flare_up_1_date",
            "flare_up_description1": "flare_up_1_description",
            "flare_up_manaegment1___1": "flare_up_1_management_community",
            "flare_up_manaegment1___2": "flare_up_1_management_inpatient",
            "flare_up_manaegment1___3": "flare_up_1_management_oral_steroids",
            "flare_up_manaegment1___4": "flare_up_1_management_asa",
            "flare_up_manaegment1___5": "flare_up_1_management_dietetics",
            "flare_up_manaegment1___99": "flare_up_1_management_other",
            "flare_up_managmnt_other1": "flare_up_1_management_other_text",
            "flare_up_timeframe2": "flare_up_2_date",
            "flare_up_description2": "flare_up_2_description",
            "flare_up_manaegment2___1": "flare_up_2_management_community",
            "flare_up_manaegment2___2": "flare_up_2_management_inpatient",
            "flare_up_manaegment2___3": "flare_up_2_management_oral_steroids",
            "flare_up_manaegment2___4": "flare_up_2_management_asa",
            "flare_up_manaegment2___5": "flare_up_2_management_dietetics",
            "flare_up_manaegment2___99": "flare_up_2_management_other",
            "flare_up_managmnt_other2": "flare_up_2_management_other_text",
            "unplanned_hospital": "unplanned_hospital_admission",
            "flare_up_comment": "flare_up_comments",
            "reason_of_use_steroid1": "steroid_use_1_reason",
            "other_reason_use_steroid1": "steroid_use_1_reason_text",
            "dt_seroid_drug_cu1": "steroid_use_1_drug",
            "steroid_other_drug_cu1": "steroid_use_1_drug_text",
            "steroid_dose1": "steroid_use_1_dose",
            "steroid_freq_of_use1": "steroid_use_1_frequency",
            "other_steroid_freofuse1": "steroid_use_1_frequency_text",
            "steroid_sd1": "steroid_use_1_start_date",
            "still_taken_steroid1": "steroid_use_1_still_taking",
            "steroid_ed1": "steroid_use_1_end_date",
            "stop_steroid_res1": "steroid_use_1_reason_stopped",
            # "steroid_change_dose1": "steroid_use_1_reason_changed",
            "other_stop_steroid_res1": "steroid_use_1_reason_changed_text",
            "reason_of_use_steroid2": "steroid_use_2_reason",
            "other_reason_use_steroid2": "steroid_use_2_reason_text",
            "dt_seroid_drug_cu2": "steroid_use_2_drug",
            "steroid_other_drug_cu2": "steroid_use_2_drug_text",
            "steroid_dose2": "steroid_use_2_dose",
            "steroid_freq_of_use2": "steroid_use_2_frequency",
            "other_steroid_freofuse2": "steroid_use_2_frequency_text",
            "steroid_sd2": "steroid_use_2_start_date",
            "still_taken_steroid2": "steroid_use_2_still_taking",
            "steroid_ed2": "steroid_use_2_end_date",
            "stop_steroid_res2": "steroid_use_2_reason_stopped",
            # "steroid_change_dose2": "steroid_use_2_reason_changed",
            "other_stop_steroid_res2": "steroid_use_2_reason_changed_text",
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
            "montreal_rev_date": "montreal_classification_date",
            "montrealcomments": "montreal_classification_comments",
            "baseline_drug_check": "baseline_previous_ibd_treatment",
            "baseline_eims___2": "baseline_eims_arthralgia",
            "baseline_eims___3": "baseline_eims_ank_spon",
            "baseline_eims___5": "baseline_eims_erythema_nodosum",
            "baseline_eims___6": "baseline_eims_pyoderma",
            "baseline_eims___10": "baseline_eims_uveitis",
            "baseline_eims___12": "baseline_eims_episcleritis",
            "baseline_eims___15": "baseline_eims_none",
            "baseline_eims_subother___99": "baseline_eims_other",
            "baseline_eims_subother___1": "baseline_eims_iritis_scleritis",
            "baseline_eims_subother___8": "baseline_eims_sacroileitis",
            "baseline_eims_subother___11": "baseline_eims_conjunctivitis",
            "baseline_eims_subother___14": "baseline_eims_angular_cheilitis",
            "baseline_eims_other": "baseline_eims_other_text",
            "baseline_record_date_5": "endoscopy_prior_to_recruitment_date",
            "endoscopy_type_2___2": "endoscopy_prior_to_recruitment_colonoscopy",
            "endoscopy_type_2___3": "endoscopy_prior_to_recruitment_flexible_sigmoidoscopy",
            "endoscopy_result2": "endoscopy_prior_to_recruitment_report",
            "mayo_total_score_2": "endoscopy_prior_to_recruitment_mayo_score",
            "uceis_total_score_2": "endoscopy_prior_to_recruitment_uceis_score",
            "baseline_record_date_6": "radiology_prior_to_recruitment_date",
            "baseline_radiology_type___3": "radiology_prior_to_recruitment_ctap",
            "baseline_radiology_type___6": "radiology_prior_to_recruitment_mri_sb",
            "baseline_radiology_type___7": "radiology_prior_to_recruitment_mri_pelvis",
            "baseline_radiology_res_dsc": "radiology_prior_to_recruitment_report",
            "baseline_record_date_7": "histology_prior_to_recruitment_date",
            "baseline_histology_res_dsc": "histology_prior_to_recruitment_report",
            "uceis_total_score": "uceis_calc",
            "cdeis_total_score": "sescd_calc",
            "est_severity": "physician_endoscopic_severity",
            "sh_num": "surgical_history_number",
            "surgery_date_ibd_sh": "surgical_history_1_date",
            "ibd_proc_type_sh": "surgical_history_1_procedure_main",
            "ibd_others_proc_type_sh": "surgical_history_1_procedure_other",
            "other_surgery_hist_ibd": "surgical_history_1_procedure_other_text",
            "baseline_sh_ibd_report": "surgical_history_1_report",
            "surgery_date_ibd_sh_2": "surgical_history_2_date",
            "ibd_proc_type_sh_2": "surgical_history_2_procedure_main",
            "ibd_others_proc_type_sh_2": "surgical_history_2_procedure_other",
            "other_surgery_hist_ibd_2": "surgical_history_2_procedure_other_text",
            "baseline_sh_ibd_report_2": "surgical_history_2_report",
            "surgery_date_ibd_sh_3": "surgical_history_3_date",
            "ibd_proc_type_sh_3": "surgical_history_3_procedure_main",
            "ibd_others_proc_type_sh_3": "surgical_history_3_procedure_other",
            "other_surgery_hist_ibd_3": "surgical_history_3_procedure_other_text",
            "baseline_sh_ibd_report_3": "surgical_history_3_report",
            "drug_level_inflxi": "ifx_level",
            "drug_level_adalimumab": "ada_level",
            "drug_level_antibody_adali": "ada_antibody",
            "drug_level_antibody_inflx": "ifx_antibody",
            "date_test_adali_inflixi": "drug_level_date",
            "faecal_test_date_2": "calprotectin_date",
            "histologycomments_si_sh": "phenotyping_comments",
            "mh_appendx1": "previous_appendicectomy",
            "mh_tonsilout1": "previous_tonsillectomy",
            "mh_appendix_date1": "appendicectomy_age",
            "mh_tonsil_date1": "tonsillectomy_age",
            "mh_1sd": "pmh_1_start_date",
            "mh_1ed": "pmh_1_end_date",
            "mh_diagnosis_1": "pmh_1_diagnosis",
            "mh_2sd": "pmh_2_start_date",
            "mh_2ed": "pmh_2_end_date",
            "mh_diagnosis_2": "pmh_2_diagnosis",
            "mh_3sd": "pmh_3_start_date",
            "mh_3ed": "pmh_3_end_date",
            "mh_diagnosis_3": "pmh_3_diagnosis",
            "mh_4sd": "pmh_4_start_date",
            "mh_4ed": "pmh_4_end_date",
            "mh_diagnosis_4": "pmh_4_diagnosis",
            "mh_5sd": "pmh_5_start_date",
            "mh_5ed": "pmh_5_end_date",
            "mh_diagnosis_5": "pmh_5_diagnosis",
            "mh_6sd": "pmh_6_start_date",
            "mh_6ed": "pmh_6_end_date",
            "mh_diagnosis_6": "pmh_6_diagnosis",
            "mh_7sd": "pmh_7_start_date",
            "mh_7ed": "pmh_7_end_date",
            "mh_diagnosis_7": "pmh_7_diagnosis",
            "mh_comments": "pmh_comments",
            "endoscopy_type___2": "endoscopy_type_colonoscopy",
            "endoscopy_type___3": "endoscopy_type_flexible_sigmoidoscopy",
            "fh_number_bs": "fh_number_siblings",
            "fh_number_kids_daughter": "fh_number_daughters",
            "fh_number_kids_son": "fh_number_sons",
            "fh_number_kids": "fh_number_children",
            "family_history_pfh": "fh_of_ibd_present",
            "fhnumber_pfh": "fh_of_ibd_number_affected",
            "relationship_pfh": "fh_1_relationship",
            "age_at_diagnosis": "fh_1_age_at_diagnosis",
            "fhdiagnosis_pfh_1": "fh_1_diagnosis",
            "fhdiagnosis_pfh_other1": "fh_1_diagnosis_other",
            "other_fhdiagnosis_oid1": "fh_1_diagnosis_other_text",
            "relationship_pfh_2": "fh_2_relationship",
            "age_at_diagnosis_2": "fh_2_age_at_diagnosis",
            "fhdiagnosis_pfh_2": "fh_2_diagnosis",
            "fhdiagnosis_pfh_other2": "fh_2_diagnosis_other",
            "other_fhdiagnosis_oid2": "fh_2_diagnosis_other_text",
            "relationship_pfh_3": "fh_3_relationship",
            "age_at_diagnosis_3": "fh_3_age_at_diagnosis",
            "fhdiagnosis_pfh_3": "fh_3_diagnosis",
            "fhdiagnosis_pfh_other3": "fh_3_diagnosis_other",
            "other_fhdiagnosis_oid3": "fh_3_diagnosis_other_text",
            "relationship_pfh_4": "fh_4_relationship",
            "age_at_diagnosis_4": "fh_4_age_at_diagnosis",
            "fhdiagnosis_pfh_4": "fh_4_diagnosis",
            "fhdiagnosis_pfh_other4": "fh_4_diagnosis_other",
            "other_fhdiagnosis_oid4": "fh_4_diagnosis_other_text",
            "relationship_pfh_5": "fh_5_relationship",
            "age_at_diagnosis_5": "fh_5_age_at_diagnosis",
            "fhdiagnosis_pfh_5": "fh_5_diagnosis",
            "fhdiagnosis_pfh_other5": "fh_5_diagnosis_other",
            "other_fhdiagnosis_oid5": "fh_5_diagnosis_other_text",
            "patdetailscomments_pfh": "fh_comments",
            "ct_abdomen_and_or_pelvis": "ct_abdomen_pelvis",
            "abdominal_uss": "uss_abdomen",
            "abdominal_x_ray": "axr",
            "radilogy_r_ctabdo_pelvic": "ct_abdomen_pelvis_report",
            "radiology_r_abdo_x_ray": "axr_report",
            "radiology_r_abdo_uss": "uss_abdomen_report",
            "radiology_r_mri_sml_bowel": "mri_small_bowel_report",
            "radiology_r_mri_pelvis": "mri_pelvis_report",
            "radiologyfindingcomments": "radiology_report_summary",
            "ibd_surgery_si": "ibd_surgery_performed",
            "surgery_date_si": "ibd_surgery_date",
            "ibd_procedure_type": "ibd_surgery_procedure",
            "ibd_procedure_type_other": "ibd_surgery_procedure_other",
            "ibd_other_specify_proc": "ibd_surgery_procedure_other_text",
            "ibd_procedure_result": "ibd_surgery_comments",
            "histologycomments_si": "ibd_surgery_histology_report",
        },
        inplace=True,
    )

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

    # df['fh_1_diagnosis_other'] = df['fh_1_diagnosis_other'].map(fh_diagnosis_other_map)
    df["fh_2_diagnosis_other"] = df["fh_2_diagnosis_other"].map(fh_diagnosis_other_map)
    df["fh_3_diagnosis_other"] = df["fh_3_diagnosis_other"].map(fh_diagnosis_other_map)
    # df['fh_4_diagnosis_other'] = df['fh_4_diagnosis_other'].map(fh_diagnosis_other_map)

    df["fh_1_relationship"] = df["fh_1_relationship"].map(fh_relationship_map)
    df["fh_2_relationship"] = df["fh_2_relationship"].map(fh_relationship_map)
    df["fh_3_relationship"] = df["fh_3_relationship"].map(fh_relationship_map)
    df["fh_4_relationship"] = df["fh_4_relationship"].map(fh_relationship_map)

    surgical_history_procedure_main_map = {
        "2": "colectomy",
        "7": "ibd_resection",
        "8": "ileocaecal_resection",
        "23": "small_bowel_resection",
        "10": "eua_perianal_fistula",
    }

    surgical_history_procedure_other_map = {
        "1": "appendicectomy",
        "3": "completion_colectomy",
        "4": "completion_proctectomy",
        "5": "pouch_excision",
        "6": "rectal_stump_excision",
        "9": "ileocolic_resection",
        "10": "ileotransverse_colectomy",
        "11": "left_hemicolectomy",
        "12": "segmental_colonic_resection",
        "13": "colovaginal_fistula_repair",
        "14": "other_segmental_resection",
        "15": "panproctocolectomy",
        "16": "panproctocolectomy_with_pouch",
        "17": "stoma_revision",
        "18": "right_hemicolectomy",
        "19": "right_hemicolectomy_with_ileal_stricturoplasty",
        "20": "right_hemicoloectomy_with_ileal_resection",
        "21": "ileocaecal_resection",
        "22": "segmental_colonic_resection",
        "24": "subtotal_colectomy",
    }

    df["surgical_history_1_procedure_main"] = df[
        "surgical_history_1_procedure_main"
    ].map(surgical_history_procedure_main_map)
    df["surgical_history_1_procedure_other"] = df[
        "surgical_history_1_procedure_other"
    ].map(surgical_history_procedure_other_map)
    df["surgical_history_2_procedure_main"] = df[
        "surgical_history_2_procedure_main"
    ].map(surgical_history_procedure_main_map)
    df["surgical_history_2_procedure_other"] = df[
        "surgical_history_2_procedure_other"
    ].map(surgical_history_procedure_other_map)
    df["surgical_history_3_procedure_main"] = df[
        "surgical_history_3_procedure_main"
    ].map(surgical_history_procedure_main_map)
    df["surgical_history_3_procedure_other"] = df[
        "surgical_history_3_procedure_other"
    ].map(surgical_history_procedure_other_map)

    df["surgical_history_1_procedure"] = df[
        [
            "surgical_history_1_procedure_main",
            "surgical_history_1_procedure_other",
            "surgical_history_1_procedure_other_text",
        ]
    ].apply(lambda x: ", ".join(x.dropna()), axis=1)
    df.drop(
        columns=[
            "surgical_history_1_procedure_main",
            "surgical_history_1_procedure_other",
            "surgical_history_1_procedure_other_text",
        ],
        inplace=True,
    )
    df["surgical_history_2_procedure"] = df[
        [
            "surgical_history_2_procedure_main",
            "surgical_history_2_procedure_other",
            "surgical_history_2_procedure_other_text",
        ]
    ].apply(lambda x: ", ".join(x.dropna()), axis=1)
    df.drop(
        columns=[
            "surgical_history_2_procedure_main",
            "surgical_history_2_procedure_other",
            "surgical_history_2_procedure_other_text",
        ],
        inplace=True,
    )
    df["surgical_history_3_procedure"] = df[
        [
            "surgical_history_3_procedure_main",
            "surgical_history_3_procedure_other",
            "surgical_history_3_procedure_other_text",
        ]
    ].apply(lambda x: ", ".join(x.dropna()), axis=1)
    df.drop(
        columns=[
            "surgical_history_3_procedure_main",
            "surgical_history_3_procedure_other",
            "surgical_history_3_procedure_other_text",
        ],
        inplace=True,
    )

    df["surgical_history_1_procedure"].replace("", pd.NA, inplace=True)
    df["surgical_history_2_procedure"].replace("", pd.NA, inplace=True)
    df["surgical_history_3_procedure"].replace("", pd.NA, inplace=True)

    df["steroid_use_1_reason"] = df["steroid_use_1_reason"].map(
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
    df["steroid_use_1_frequency"] = df["steroid_use_1_frequency"].map(
        {
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
    )
    df["steroid_use_1_still_taking"] = df["steroid_use_1_still_taking"].map(
        {"1": "yes", "0": "no"}
    )
    df["steroid_use_1_reason_stopped"] = df["steroid_use_1_reason_stopped"].map(
        {
            "1": "primary_non_response",
            "2": "secondary_non_response",
            "3": "significant_dose_change_of_existing_steroid",
            "9": "intolerance",
            "7": "adverse_effects",
            "10": "confirmed_immunogenicity",
            "99": "other",
        }
    )

    df["steroid_use_2_reason"] = df["steroid_use_2_reason"].map(
        {"1": "flare_up", "99": "other"}
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
    df["steroid_use_2_frequency"] = df["steroid_use_2_frequency"].map(
        {
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
    )
    df["steroid_use_2_still_taking"] = df["steroid_use_2_still_taking"].map(
        {"1": "yes", "0": "no"}
    )
    df["steroid_use_2_reason_stopped"] = df["steroid_use_2_reason_stopped"].map(
        {
            "1": "primary_non_response",
            "2": "secondary_non_response",
            "3": "significant_dose_change_of_existing_steroid",
            "9": "intolerance",
            "7": "adverse_effects",
            "10": "confirmed_immunogenicity",
            "99": "other",
        }
    )

    df["new_oral_steroids_since_last_visit"] = df[
        "new_oral_steroids_since_last_visit"
    ].map({"1": "yes", "0": "no", "3": "ongoing_since_last_visit"})

    df["study_group_name"] = df["study_group_name"].map(
        {
            "1": "cd",
            "2": "uc",
        }
    )

    df["sex"] = df["sex"].map(
        {
            "1": "male",
            "2": "female",
        }
    )

    df["smoking_status"] = df["smoking_status"].map(
        {
            "1": "smoker",
            "2": "ex_smoker",
            "3": "non_smoker",
        }
    )

    df["when_smoking_stopped_units"] = df["when_smoking_stopped_units"].map(
        {
            "1": "weeks",
            "2": "months",
            "3": "years",
        }
    )

    df["sccai_general_well_being"] = df["sccai_general_well_being"].map(
        {
            "0": "very_well",
            "1": "slightly_below_par",
            "2": "poor",
            "3": "very_poor",
            "4": "terrible",
        }
    )

    df["sccai_bowel_frequency_day"] = df["sccai_bowel_frequency_day"].map(
        {"0": "0-3", "1": "4-6", "2": "7-9", "3": ">9"}
    )

    df["sccai_bowel_frequency_night"] = df["sccai_bowel_frequency_night"].map(
        {
            "0": "0",
            "1": "1-3",
            "2": "4-6",
        }
    )

    df["sccai_urgency"] = df["sccai_urgency"].map(
        {
            "0": "none",
            "1": "hurry",
            "2": "immediately",
            "3": "incontinence",
        }
    )

    df["sccai_blood_in_stool"] = df["sccai_blood_in_stool"].map(
        {
            "0": "none",
            "1": "trace",
            "2": "occasionally_frank",
            "3": "usually_frank",
        }
    )

    df["hbi_abdominal_mass"] = df["hbi_abdominal_mass"].map(
        {
            "0": "none",
            "1": "dubious",
            "2": "definite",
            "3": "definite_and_tender",
        }
    )

    df["hbi_general_well_being"] = df["hbi_general_well_being"].map(
        {
            "0": "very_well",
            "1": "slightly_below_par",
            "2": "poor",
            "3": "very_poor",
            "4": "terrible",
        }
    )

    df["hbi_abdominal_pain"] = df["hbi_abdominal_pain"].map(
        {
            "0": "none",
            "1": "mild",
            "2": "moderate",
            "3": "severe",
        }
    )

    df["hbi_liquid_stools_present"] = df["hbi_liquid_stools_present"].map(
        {
            "0": "no",
            "1": "yes",
        }
    )

    df["mayo_stool_frequency"] = df["mayo_stool_frequency"].map(
        {
            "0": "normal",
            "1": "1-2_above_normal",
            "2": "3-4_above_normal",
            "3": ">5_above_normal",
        }
    )

    df["mayo_rectal_bleeding"] = df["mayo_rectal_bleeding"].map(
        {
            "0": "none",
            "1": "less_than_half",
            "2": "more_than_half",
            "3": "blood_alone",
        }
    )

    df["mayo_physician_global_assessment"] = df["mayo_physician_global_assessment"].map(
        {
            "0": "normal",
            "1": "mild",
            "2": "moderate",
            "3": "severe",
        }
    )

    df["new_flare_up"] = df["new_flare_up"].map(
        {
            "0": "no",
            "1": "yes",
            "3": "ongoing_from_previous_visit",
        }
    )

    df["unplanned_hospital_admission"] = df["unplanned_hospital_admission"].map(
        {
            "0": "no",
            "1": "yes",
        }
    )

    df["steroid_use_1_reason"] = df["steroid_use_1_reason"].map(
        {
            "1": "flare_up",
            "99": "other",
        }
    )

    df["redcap_event_name"] = df["redcap_event_name"].map(
        {
            "timepoint_1_arm_1": "timepoint_1",
            "timepoint_2_arm_1": "timepoint_2",
            "timepoint_3_arm_1": "timepoint_3",
            "timepoint_4_arm_1": "timepoint_4",
            "timepoint_5_arm_1": "timepoint_5",
        }
    )

    df["physician_global_assessment"] = df["physician_global_assessment"].map(
        {
            "1": "remission",
            "2": "mild",
            "3": "moderate",
            "4": "severe",
        }
    )

    df["disease_activity"] = df["disease_activity"].map(
        {
            "1": "biochem_remission",
            "2": "remission",
            "3": "active",
            "4": "biochem_active",
            "5": "not_applicable",
        }
    )  # this field almost maps to ibd_status in gi-damps but differ in highly_active vs biochem_active

    df["change_in_montreal"] = df["change_in_montreal"].map(
        {
            "0": "no",
            "1": "yes",
        }
    )

    df["montreal_cd_location"] = df["montreal_cd_location"].map(
        {"0": "L1", "1": "L2", "2": "L3"}
    )

    df["montreal_cd_behaviour"] = df["montreal_cd_behaviour"].map(
        {"0": "B1", "1": "B2", "2": "B3"}
    )

    df["montreal_uc_extent"] = df["montreal_uc_extent"].map(
        {"0": "E1", "1": "E2", "2": "E3"}
    )

    df["montreal_uc_severity"] = df["montreal_uc_severity"].map(
        {"0": "S0", "1": "S1", "2": "S2", "3": "S3"}
    )

    df["study_center"] = df["study_id"].apply(
        lambda x: "glasgow"
        if "91-" in x
        else (
            "dundee"
            if "92-" in x
            else (
                "edinburgh" if "90-" in x else ("fate_cd" if "191-" in x else "unknown")
            )
        )
    )

    # Data harmonization
    df.rename(columns={"study_group_name": "study_group"}, inplace=True)
    df["study_id"] = df["study_id"].apply(lambda x: f"MID-{x}")

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


@asset(
    description="Creates abbreviated music demographics dataframe", group_name="music"
)
def music_demographics_dataframe(
    context: AssetExecutionContext,
    music_cleaned_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    df = music_cleaned_dataframe

    demographics_df = df[df["redcap_event_name"] == "timepoint_1"]

    demographics_columns = [
        "study_id",
        "redcap_event_name",
        "age",
        "sex",
        "study_group",
        "diagnosis_comments",
        "date_of_diagnosis",
        "age_at_diagnosis",
        "smoking_status",
        "when_smoking_stopped",
        "when_smoking_stopped_units",
        "height",
        "weight",
        "bmi",
        "has_active_symptoms",
        "visit_date",
        "physician_global_assessment",
        "disease_activity",
        "symptoms_description",
        "cucq_total",
        "change_in_montreal",
        "disease_activity_score_date",
        "sccai_total",
        "hbi_total",
        "disease_activity_score_comments",
        "mayo_total",
        "montreal_classification_date",
        "montreal_cd_location",
        "montreal_cd_behaviour",
        "montreal_perianal",
        "montreal_upper_gi",
        "montreal_uc_extent",
        "montreal_uc_severity",
        "montreal_classification_comments",
        "baseline_previous_ibd_treatment",
        "baseline_eims_arthralgia",
        "baseline_eims_ank_spon",
        "baseline_eims_erythema_nodosum",
        "baseline_eims_pyoderma",
        "baseline_eims_uveitis",
        "baseline_eims_episcleritis",
        "baseline_eims_none",
        "baseline_eims_iritis_scleritis",
        "baseline_eims_sacroileitis",
        "baseline_eims_conjunctivitis",
        "baseline_eims_angular_cheilitis",
        "baseline_eims_other",
        "baseline_eims_other_text",
        "baseline_surgical_history",
        "endoscopy_prior_to_recruitment_date",
        "endoscopy_prior_to_recruitment_colonoscopy",
        "endoscopy_prior_to_recruitment_flexible_sigmoidoscopy",
        "endoscopy_prior_to_recruitment_report",
        "endoscopy_prior_to_recruitment_mayo_score",
        "endoscopy_prior_to_recruitment_uceis_score",
        "radiology_prior_to_recruitment_date",
        "radiology_prior_to_recruitment_ctap",
        "radiology_prior_to_recruitment_mri_sb",
        "radiology_prior_to_recruitment_mri_pelvis",
        "radiology_prior_to_recruitment_report",
        "histology_prior_to_recruitment_date",
        "histology_prior_to_recruitment_report",
        "surgical_history_number",
        "surgical_history_1_date",
        "surgical_history_1_report",
        "surgical_history_2_date",
        "surgical_history_2_report",
        "surgical_history_3_date",
        "surgical_history_3_report",
        "phenotyping_comments",
        "previous_appendicectomy",
        "previous_tonsillectomy",
        "appendicectomy_age",
        "tonsillectomy_age",
        "pmh_1_start_date",
        "pmh_1_end_date",
        "pmh_1_diagnosis",
        "pmh_2_start_date",
        "pmh_2_end_date",
        "pmh_2_diagnosis",
        "pmh_3_start_date",
        "pmh_3_end_date",
        "pmh_3_diagnosis",
        "pmh_4_start_date",
        "pmh_4_end_date",
        "pmh_4_diagnosis",
        "pmh_5_start_date",
        "pmh_5_end_date",
        "pmh_5_diagnosis",
        "pmh_comments",
        "fh_number_brothers",
        "fh_number_sisters",
        "fh_number_siblings",
        "fh_number_daughters",
        "fh_number_sons",
        "fh_number_children",
        "fh_of_ibd_present",
        "fh_of_ibd_number_affected",
        "fh_1_relationship",
        "fh_1_age_at_diagnosis",
        "fh_1_diagnosis",
        "fh_2_relationship",
        "fh_2_age_at_diagnosis",
        "fh_2_diagnosis",
        "fh_2_diagnosis_other",
        "fh_2_diagnosis_other_text",
        "fh_3_relationship",
        "fh_3_age_at_diagnosis",
        "fh_3_diagnosis",
        "fh_3_diagnosis_other",
        "fh_4_relationship",
        "fh_4_age_at_diagnosis",
        "fh_4_diagnosis",
        "fh_comments",
        "baseline_5asa",
        "baseline_mtx",
        "baseline_ifx",
        "baseline_ada",
        "baseline_aza",
        "baseline_mp",
        "baseline_uste",
        "baseline_vedo",
        "baseline_goli",
        "baseline_tofa",
        "baseline_filgo",
        "baseline_risa",
        "surgical_history_1_procedure",
        "surgical_history_2_procedure",
        "surgical_history_3_procedure",
    ]
    demographics_df = demographics_df[demographics_columns]

    rows, columns = demographics_df.shape
    context.add_output_metadata(
        {
            "dagster/row_count": rows,
            "column_count": columns,
            "columns": demographics_df.columns.to_list(),
            "preview": MetadataValue.md(demographics_df.head().to_markdown()),
        }
    )

    return demographics_df


@asset(
    group_name="music",
    description="Stores MUSIC abbreviated demographics data in GTrac Dataset model",
)
def store_music_demographics_in_gtrac(
    music_demographics_dataframe: pd.DataFrame, gtrac: GTracResource
) -> MaterializeResult:
    df = music_demographics_dataframe
    json = df.to_json(orient="records")

    data = {
        "study_name": "music",
        "name": "music_demographics",
        "description": "Abbreviated version of the main MUSIC dataframe consisting of selected demographics columns. Use this to make demographics table. Each row represents a single participant at timepoint 1.",
        "json": json,
    }

    response = gtrac.submit_data(data)
    return MaterializeResult(
        metadata={
            "status_code": str(response.status_code),
        }
    )

```
