# GI-DAMPs

```py title="assets/gidamps.py"
import datetime

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
    description="Fetches GI-DAMPs data from IGMM RedCap Server",
    group_name="gidamps",
)
def gidamps_raw_dataframe() -> pd.DataFrame:
    """
    Fetches raw data from the GIDAMPS REDCap API and returns it as a pandas DataFrame.
    The function performs the following steps:
    1. Retrieves the GIDAMPS API token from environment variables.
    2. Defines the REDCap API URL and the data payload for the API request.
    3. Sends a POST request to the REDCap API to fetch the data.
    4. Converts the JSON response into a pandas DataFrame.
    5. Drops specific columns from the DataFrame that are not needed.
    Returns:
        pd.DataFrame: A pandas DataFrame containing the raw data from the GIDAMPS REDCap API.
    """

    GIDAMPS_API_TOKEN = EnvVar("GIDAMPS_API_TOKEN").get_value()
    gidamps_redcap_url = "https://ecrf.igmm.ed.ac.uk/api/"
    redcap_api_data = {
        "token": f"{GIDAMPS_API_TOKEN}",
        "content": "record",
        "action": "export",
        "format": "json",
        "type": "flat",
        "csvDelimiter": "",
        "rawOrLabel": "raw",
        "rawOrLabelHeaders": "raw",
        "exportCheckboxLabel": "false",
        "exportSurveyFields": "false",
        "exportDataAccessGroups": "false",
        "returnFormat": "json",
    }
    response = requests.post(gidamps_redcap_url, data=redcap_api_data)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame.from_records(data)
    df.drop(
        columns=[
            "email",
            "chi_no",
            "consent",
            "initial",
            "dob",
            "legacy_study_id",
            "patient_details_complete",
            "pd_gi_participant_category",
            "registration_location",
            "date_enrolledconsent",
            "data_entry_date",
            "study_group",
            "study_group_hc",
            "blood_experiment",
            "faecal_experiment",
            "biopsy_experiment",
            "bloodtestdate_as_lbt",
            "blood_sample_collected___5",
            "blood_sample_collected___6",
            "blood_sample_collected___3",
            "blood_sample_collected___4",
            "blood_sample_collected___100",
            "blood_sample_collected___200",
            "blood_sample_collected___99",
            "blood_sample_collected___2",
            "blood_sample_collected___1",
            "blood_sample_collected____1000",
            "blood_sample_optinal_set___1",
            "blood_sample_optinal_set____1000",
            "blood_sample_additional___1",
            "blood_sample_additional___2",
            "blood_sample_additional____1000",
            "faecal_test_date",
            "faecal_sample_collected___1",
            "faecal_sample_collected___2",
            "faecal_sample_collected___3",
            "faecal_sample_collected___4",
            "faecal_sample_collected___99",
            "faecal_sample_collected____1000",
            "sampls_date_experiment4",
            "biopsy_sample_collected___1",
            "biopsy_sample_collected___2",
            "biopsy_sample_collected___99",
            "biopsy_sample_collected____1000",
            "sampling_complete",
            "baseline_eims____1000",
            "sccai_complications____1000",
            "hbicomplications____1000",
            "adalimumab_test",
            "infliximab_test",
            "vedolizumab_test",
            "ustekinumab_test",
            "drug_level_uste",
            "drug_level_antibody_uste",
            "drug_level_vedo",
            "drug_level_antibody_vedo",
            "endoscopy_yn",
            "endoscopy_type____1000",
            "gidamps_participant_questionnaire_complete",
            "baseline_mont_cd_loc____1000",
            "baseline_mont_cd_beh____1000",
            "radiology",
            "ibd_background_clinician_complete",
        ],
        inplace=True,
    )
    return df


@asset(
    description="Data cleaning - Renames columns and maps values.", group_name="gidamps"
)
def gidamps_cleaned_dataframe(
    context: AssetExecutionContext, gidamps_raw_dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Cleans and transforms the raw GIDAMPS dataframe.
    This function performs the following operations:
    1. Renames columns to more readable names.
    2. Converts specified columns to numeric types, coercing errors.
    3. Converts date columns to datetime objects and calculates diagnosis duration.
    4. Maps categorical columns to more readable values.
    5. Creates new columns based on existing data.
    6. Drops unnecessary columns.
    7. Replaces empty strings with NaN values.
    Args:
        gidamps_raw_dataframe (pd.DataFrame): The raw dataframe containing GIDAMPS data.
    Returns:
        pd.DataFrame: The cleaned and transformed dataframe.
    """
    df = gidamps_raw_dataframe

    df.rename(
        columns={
            "bl_new_diagnosis": "new_diagnosis_of_ibd",
            "smokeryn1": "smoking_status",
            "bmi_height": "height",
            "bmi_weight": "weight",
            "diagnosis_age": "age_at_diagnosis",
            "smokeryn1_y": "is_smoker",
            "patient_active_symptomyn1": "has_active_symptoms",
            "antibiotics": "sampling_abx",
            "steroids": "sampling_steroids",
            "haematocrit_lab": "haematocrit",
            "neutrophils_lab": "neutrophils",
            "lymphocytes_lab": "lymphocytes",
            "monocytes_lab": "monocytes",
            "eosinophils_lab": "eosinophils",
            "basophils_lab": "basophils",
            "plt_lab": "platelets",
            "urea_lab": "urea",
            "creatinine_lab": "creatinine",
            "sodium_lab": "sodium",
            "potassium_lab": "potassium",
            "egfr_lab": "egfr",
            "faecal_test_date_2": "calprotectin_date",
            "drug_level_inflxi": "ifx_level",
            "drug_level_adalimumab": "ada_level",
            "drug_level_antibody_adali": "ada_antibody",
            "drug_level_antibody_inflx": "ifx_antibody",
            "baseline_mont_uc_extent": "montreal_uc_extent",
            "baseline_mont_seve_uc": "montreal_uc_severity",
            "baseline_eims___2": "baseline_eims_arthralgia",
            "baseline_eims___3": "baseline_eims_ank_spon",
            "baseline_eims___5": "baseline_eims_erythema_nodosum",
            "baseline_eims___6": "baseline_eims_pyoderma",
            "baseline_eims___10": "baseline_eims_uveitis",
            "baseline_eims___12": "baseline_eims_episcleritis",
            "baseline_eims___8": "baseline_eims_sacroileitis",
            "baseline_eims___15": "baseline_eims_none",
            "sccai_complications___1": "sccai_arthralgia",
            "sccai_complications___2": "sccai_uveitis",
            "sccai_complications___3": "sccai_erythema_nodosum",
            "sccai_complications___4": "sccai_pyoderma",
            "hbicomplications___1": "hbi_arthralgia",
            "hbicomplications___2": "hbi_uveitis",
            "hbicomplications___3": "hbi_erythema_nodosum",
            "hbicomplications___4": "hbi_apthous_ulcers",
            "hbicomplications___5": "hbi_pyoderma",
            "hbicomplications___6": "hbi_anal_fissures",
            "hbicomplications___7": "hbi_new_fistula",
            "hbicomplications___8": "hbi_abscess",
            "baseline_gi_symptoms_desc": "symptoms_description",
            "sccai_bowel_freqday": "sccai_bowel_frequency_day",
            "sccai_bowel_frequency_nigh": "sccai_bowel_frequency_night",
            "sccai_urgency_of_defecatio": "sccai_urgency",
            "hbinumber_of_liquid_stools": "hbi_liquid_stools",
            "hbiabdominal_mass1": "hbi_abdominal_mass",
            "hbigeneral_well_being_as": "hbi_general_well_being",
            "hbiabdominal_pain": "hbi_abdominal_pain",
            "blood_test_date_red": "nhs_bloods_date",
            "date_test_adali_inflixi": "drug_level_date",
            "endoscopy_result_endcospy": "endoscopy_report",
            "histopathology_report_text": "pathology_report",
            "ct_abdomen_and_or_pelvis": "ct_abdomen",
            "radilogy_r_ctabdo_pelvic": "ct_abdomen_report",
            "radiology_r_mri_sml_bowel": "mri_small_bowel_report",
            "radiology_r_mri_pelvis": "mri_pelvis_report",
            "comment_if_any_of_these_qu": "participant_questionnaire_comments",
            "mh_appendx1": "previous_appendicectomy",
            "mh_tonsilout1": "previous_tonsillectomy",
            "mh_tonsil_date1": "age_or_year_of_tonsillectomy",
            "mh_appendix_date1": "age_or_year_of_appendicectomy",
            "fhdiagnosis_pfh_1": "family_history_diagnosis",
            "relationship_pfh": "family_history_relationship",
            "family_history_pfh": "family_history_of_ibd",
            "gi_q1": "giq_ethnicity",
            "gi_q1_other_3": "giq_ethicity_text",
            "q_hc_goodhealth": "giq_are_you_in_good_health",
            "gi_q1_other_2": "giq_good_health_text",
            "q_hc_longterm_medication": "giq_long_term_medication",
            "gi_q1_other": "giq_long_term_medication_text",
            "q3_gi": "giq_smoking_status_at_diagnosis",
            "q5_gi": "giq_strenous_exercise_last_48h",
            "q5_gi_yes": "giq_strenous_exercise_last_48h_text",
            "q4_gi": "giq_do_you_drink_alcohol",
            "q4_gi_yes": "giq_alcohol_consumption",
        },
        inplace=True,
    )

    columns_to_convert = [
        "study_group_name",
        "baseline_recruitment_type",
        "sex",
        "ibd_status",
        "new_diagnosis_of_ibd",
        "smoking_status",
        "sccai_general_well_being",
        "sccai_bowel_frequency_day",
        "sccai_bowel_frequency_night",
        "sccai_urgency",
        "sccai_blood_in_stool",
        "montreal_uc_extent",
        "montreal_uc_severity",
        "hbi_abdominal_mass",
        "hbi_general_well_being",
        "hbi_abdominal_pain",
        "endoscopy_type___1",
        "endoscopy_type___2",
        "endoscopy_type___3",
        "baseline_mont_cd_loc___0",
        "baseline_mont_cd_loc___1",
        "baseline_mont_cd_loc___2",
        "baseline_mont_cd_loc___3",
        "baseline_mont_cd_beh___0",
        "baseline_mont_cd_beh___1",
        "baseline_mont_cd_beh___2",
        "baseline_mont_cd_beh___3",
        "ct_abdomen",
        "mri_small_bowel",
        "mri_pelvis",
        "ada_antibody",
        "ifx_antibody",
        "past_ibd_surgery",
        "ifx",
        "ciclo",
        "aza",
        "mp",
        "mtx",
        "ada",
        "uste",
        "vedo",
        "filgo",
        "risa",
        "upa",
        "golim",
        "tofa",
        "previous_appendicectomy",
        "family_history_of_ibd",
        "giq_smoking_status_at_diagnosis",
        "giq_alcohol_consumption",
        "family_history_diagnosis",
        "giq_ethnicity",
    ]
    df[columns_to_convert] = df[columns_to_convert].apply(
        pd.to_numeric, errors="coerce"
    )

    df["diagnosis_duration_in_days"] = (
        pd.to_datetime(datetime.date.today()) - pd.to_datetime(df["date_of_diagnosis"])
    ).dt.days

    df["ct_abdomen"] = df["ct_abdomen"].map({1: 1, 2: 0})
    df["mri_small_bowel"] = df["mri_small_bowel"].map({1: 1, 2: 0})
    df["mri_pelvis"] = df["mri_pelvis"].map({1: 1, 2: 0})
    df["past_ibd_surgery"] = df["past_ibd_surgery"].map({1: 1, 2: 0})
    df["ifx"] = df["ifx"].map({1: 1, 2: 0})
    df["ciclo"] = df["ciclo"].map({1: 1, 2: 0})
    df["previous_appendicectomy"] = df["previous_appendicectomy"].map({1: 1, 2: 0})

    df["family_history_of_ibd"] = df["family_history_of_ibd"].map(
        {1: "yes", 2: "no", 3: "not_available"}
    )
    df["giq_smoking_status_at_diagnosis"] = df["giq_smoking_status_at_diagnosis"].map(
        {1: "yes", 2: "no", 3: "unsure"}
    )
    df["giq_alcohol_consumption"] = df["giq_alcohol_consumption"].map(
        {
            1: "most_days",
            2: "weekends_only",
            3: "once_or_twice_a_week",
            4: "once_or_twice_a_month",
            5: "once_or_twice_a_year",
        }
    )
    df["family_history_diagnosis"] = df["family_history_diagnosis"].map(
        {
            6: "cd",
            7: "uc",
            9: "ibdu",
            10: "possible_cd",
            11: "possible_uc",
            12: "possible_ibdu",
            99: "other_diagnosis",
        }
    )
    df["giq_ethnicity"] = df["giq_ethnicity"].map(
        {1: "white_european", 99: "other_see_text"}
    )
    df["ada_antibody"] = df["ada_antibody"].map(
        {1: "<10", 2: "10-40", 3: "40-200", 4: ">200", 5: "not_tested"}
    )
    df["ifx_antibody"] = df["ifx_antibody"].map(
        {1: "<10", 2: "10-40", 3: "40-200", 4: ">200", 5: "not_tested"}
    )
    df["study_group_name"] = df["study_group_name"].map(
        {
            1: "cd",
            2: "uc",
            3: "ibdu",
            4: "non_ibd",
            5: "await_dx",
            6: "hc",
        }
    )
    df["baseline_recruitment_type"] = df["baseline_recruitment_type"].map(
        {
            1: "endoscopy",
            2: "outpatient",
            3: "inpatient",
        }
    )
    df["sex"] = df["sex"].map({1: "male", 2: "female"})
    df["ibd_status"] = df["ibd_status"].map(
        {
            0: "biochem_remission",
            1: "remission",
            2: "active",
            3: "highly_active",
            4: "not_applicable",
        }
    )

    df["new_diagnosis_of_ibd"] = df["new_diagnosis_of_ibd"].map(
        {
            1: "yes",
            0: "no",
        }
    )

    df["smoking_status"] = df["smoking_status"].map(
        {
            1: "smoker",
            2: "ex_smoker",
            3: "non_smoker",
        }
    )

    df["sccai_general_well_being"] = df["sccai_general_well_being"].map(
        {
            0: "very_well",
            1: "slightly_below_par",
            2: "poor",
            3: "very_poor",
            4: "terrible",
        }
    )
    df["sccai_bowel_frequency_day"] = df["sccai_bowel_frequency_day"].map(
        {0: "0-3", 1: "4-6", 2: "7-9", 3: ">9"}
    )
    df["sccai_bowel_frequency_night"] = df["sccai_bowel_frequency_night"].map(
        {
            0: "0",
            1: "1-3",
            2: "4-6",
        }
    )
    df["sccai_urgency"] = df["sccai_urgency"].map(
        {
            0: "none",
            1: "hurry",
            2: "immediately",
            3: "incontinence",
        }
    )
    df["sccai_blood_in_stool"] = df["sccai_blood_in_stool"].map(
        {
            0: "none",
            1: "trace",
            2: "occasionally_frank",
            3: "usually_frank",
        }
    )
    df["hbi_abdominal_mass"] = df["hbi_abdominal_mass"].map(
        {
            0: "none",
            1: "dubious",
            2: "definite",
            3: "definite_and_tender",
        }
    )
    df["hbi_general_well_being"] = df["hbi_general_well_being"].map(
        {
            0: "very_well",
            1: "slightly_below_par",
            2: "poor",
            3: "very_poor",
            4: "terrible",
        }
    )
    df["hbi_abdominal_pain"] = df["hbi_abdominal_pain"].map(
        {
            0: "none",
            1: "mild",
            2: "moderate",
            3: "severe",
        }
    )

    df["montreal_uc_extent"] = df["montreal_uc_extent"].map({0: "E1", 1: "E2", 2: "E3"})
    df["montreal_uc_severity"] = df["montreal_uc_severity"].map(
        {0: "S0", 1: "S1", 2: "S2", 3: "S3"}
    )

    df.loc[df["baseline_mont_cd_beh___0"] == 1, "montreal_cd_behaviour"] = "B1"
    df.loc[df["baseline_mont_cd_beh___1"] == 1, "montreal_cd_behaviour"] = "B2"
    df.loc[df["baseline_mont_cd_beh___2"] == 1, "montreal_cd_behaviour"] = "B3"
    df.loc[df["baseline_mont_cd_beh___3"] == 1, "montreal_perianal"] = 1
    df.loc[df["baseline_mont_cd_loc___0"] == 1, "montreal_cd_location"] = "L1"
    df.loc[df["baseline_mont_cd_loc___1"] == 1, "montreal_cd_location"] = "L2"
    df.loc[df["baseline_mont_cd_loc___2"] == 1, "montreal_cd_location"] = "L3"
    df.loc[df["baseline_mont_cd_loc___3"] == 1, "montreal_upper_gi"] = 1

    df.loc[df["endoscopy_type___1"] == 1, "endoscopy_type"] = "other"
    df.loc[df["endoscopy_type___2"] == 1, "endoscopy_type"] = "colonoscopy"
    df.loc[df["endoscopy_type___3"] == 1, "endoscopy_type"] = "flexi_sig"

    df.loc[df["aza"] == 1, "baseline_thiopurine_exposure"] = 1
    df.loc[df["mp"] == 1, "baseline_thiopurine_exposure"] = 1

    df.loc[df["ada"] == 1, "baseline_anti_tnf_exposure"] = 1
    df.loc[df["ifx"] == 1, "baseline_anti_tnf_exposure"] = 1
    df.loc[df["golim"] == 1, "baseline_anti_tnf_exposure"] = 1

    df.loc[df["ada"] == 1, "baseline_biologic_exposure"] = 1
    df.loc[df["ifx"] == 1, "baseline_biologic_exposure"] = 1
    df.loc[df["golim"] == 1, "baseline_biologic_exposure"] = 1
    df.loc[df["uste"] == 1, "baseline_biologic_exposure"] = 1
    df.loc[df["vedo"] == 1, "baseline_biologic_exposure"] = 1
    df.loc[df["filgo"] == 1, "baseline_biologic_exposure"] = 1
    df.loc[df["risa"] == 1, "baseline_biologic_exposure"] = 1
    df.loc[df["upa"] == 1, "baseline_biologic_exposure"] = 1
    df.loc[df["tofa"] == 1, "baseline_biologic_exposure"] = 1

    df.loc[df["upa"] == 1, "baseline_jak_exposure"] = 1
    df.loc[df["tofa"] == 1, "baseline_jak_exposure"] = 1
    df.loc[df["filgo"] == 1, "baseline_jak_exposure"] = 1
    cols_to_fill = [
        "baseline_thiopurine_exposure",
        "baseline_anti_tnf_exposure",
        "baseline_biologic_exposure",
        "baseline_jak_exposure",
    ]
    df[cols_to_fill] = df[cols_to_fill].fillna(0)

    df.drop(
        columns=[
            "baseline_mont_cd_loc___0",
            "baseline_mont_cd_loc___1",
            "baseline_mont_cd_loc___2",
            "baseline_mont_cd_loc___3",
            "baseline_mont_cd_beh___0",
            "baseline_mont_cd_beh___1",
            "baseline_mont_cd_beh___2",
            "baseline_mont_cd_beh___3",
            "endoscopy_type___1",
            "endoscopy_type___2",
            "endoscopy_type___3",
        ],
        inplace=True,
    )

    df["study_center"] = df["study_id"].apply(
        lambda x: "glasgow"
        if "136-" in x
        else ("dundee" if "138-" in x else "edinburgh")
    )
    # Data Harmonization
    df.rename(columns={"study_group_name": "study_group"}, inplace=True)

    df.replace(r"^\s*$", np.nan, regex=True, inplace=True)

    rows, columns = df.shape
    context.add_output_metadata(
        {
            "dagster/row_count": rows,
            "column_count": columns,
            "columns": df.columns.to_list(),
            "preview": MetadataValue.md(df.head(10).to_markdown()),
        }
    )

    return df


@asset(description="Creates demographics dataframe", group_name="gidamps")
def gidamps_demographics_dataframe(
    context: AssetExecutionContext,
    gidamps_cleaned_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Filters the given GIDAMPS cleaned dataframe to produce a demographics dataframe.
    This function removes rows where the 'redcap_repeat_instrument' column has the values 'sampling' or 'cucq32'.
    It also drops columns that contain only NaN values.
    """
    df = gidamps_cleaned_dataframe
    demographics_df = df[df["redcap_repeat_instrument"] != "sampling"]
    demographics_df = demographics_df[
        demographics_df["redcap_repeat_instrument"] != "cucq32"
    ]
    demographics_df.dropna(axis=1, how="all", inplace=True)

    rows, columns = demographics_df.shape
    context.add_output_metadata(
        {
            "dagster/row_count": rows,
            "column_count": columns,
            "columns": demographics_df.columns.to_list(),
            "preview": MetadataValue.md(demographics_df.head(10).to_markdown()),
        }
    )
    return demographics_df


@asset(
    description="Creates sampling dataframe",
    group_name="gidamps",
)
def gidamps_sampling_dataframe(
    context: AssetExecutionContext, gidamps_cleaned_dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Processes and merges different subsets of a given DataFrame based on specific conditions.
    Args:
        gidamps_cleaned_dataframe (pd.DataFrame): The input DataFrame containing GIDAMPS data.
    Returns:
        pd.DataFrame: The processed and merged DataFrame.
    The function performs the following steps:
    1. Filters out rows where 'redcap_repeat_instrument' is 'sampling' or 'cucq32' to create a demographics DataFrame.
    2. Drops columns with all NaN values from the demographics DataFrame.
    3. Creates separate DataFrames for 'sampling' and 'cucq32' instruments.
    4. Drops columns with all NaN values from the 'sampling' and 'cucq32' DataFrames.
    5. Drops specific columns from the 'sampling' and 'cucq32' DataFrames.
    6. Renames the 'cucq_date' column to 'sampling_date' in the 'cucq32' DataFrame.
    7. Merges the 'sampling' DataFrame with the demographics DataFrame on 'study_id'.
    8. Merges the resulting DataFrame with the 'cucq32' DataFrame on 'study_id' and 'sampling_date'.
    Note:
        The function assumes that the input DataFrame contains the columns 'redcap_repeat_instrument',
        'study_id', 'cucq_date', and other columns mentioned in the code.
    """

    df = gidamps_cleaned_dataframe
    demographics_df = df[df["redcap_repeat_instrument"] != "sampling"]
    demographics_df = demographics_df[
        demographics_df["redcap_repeat_instrument"] != "cucq32"
    ]
    demographics_df.dropna(axis=1, how="all", inplace=True)
    sampling_df = df[df["redcap_repeat_instrument"] == "sampling"].copy()
    cucq_df = df[df["redcap_repeat_instrument"] == "cucq32"].copy()
    sampling_df.dropna(axis=1, how="all", inplace=True)
    cucq_df.dropna(axis=1, how="all", inplace=True)
    cols_to_drop = [
        "baseline_thiopurine_exposure",
        "baseline_anti_tnf_exposure",
        "baseline_biologic_exposure",
        "baseline_jak_exposure",
        "redcap_repeat_instrument",
        "study_center",
    ]
    sampling_df.drop(columns=cols_to_drop, inplace=True)
    cucq_df.drop(columns=cols_to_drop, inplace=True)
    cucq_df.drop(columns=["redcap_repeat_instance"], inplace=True)
    cucq_df.rename(columns={"cucq_date": "sampling_date"}, inplace=True)
    merged_df = pd.merge(sampling_df, demographics_df, how="left", on="study_id")
    merged_df = pd.merge(
        merged_df, cucq_df, how="left", on=["study_id", "sampling_date"]
    )

    rows, columns = merged_df.shape
    context.add_output_metadata(
        {
            "dagster/row_count": rows,
            "column_count": columns,
            "columns": merged_df.columns.to_list(),
            "preview": MetadataValue.md(merged_df.head(10).to_markdown()),
        }
    )
    return merged_df

```
