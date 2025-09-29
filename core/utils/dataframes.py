# /Users/chershiongchuah/Developer/musicsamples/core/utils/dataframes.py
# This module provides dataframe manipulation and pivot creation utilities.
# It processes pandas dataframes for sorting, pivoting, and data transformation.

import pandas as pd
from django.db.models import QuerySet
from django_pandas.io import read_frame


def retrieve_center_number(row):
    study_id = row.name[0]
    study_id = str(study_id)
    return str.split(study_id, "-")[1]


def retrieve_patient_number(row):
    study_id = row.name[0]
    study_id = str(study_id)
    return str.split(study_id, "-")[2]


def sort_music_dataframe(df: pd.DataFrame):
    """
    Takes in music or mini_music dataframes and
    sorts by center and study_id
    """
    df["center_number"] = df.apply(retrieve_center_number, axis=1)
    df["patient_number"] = df.apply(retrieve_patient_number, axis=1)
    df["patient_number"] = pd.to_numeric(df["patient_number"])
    df.sort_values(by=["center_number", "patient_number", "sample_date"], inplace=True)
    df.drop(["center_number", "patient_number"], axis=1, inplace=True)
    return df


def create_sample_type_pivot(qs: QuerySet, study_name: str):
    """
    Takes in a samples queryset, study_name and
    creates a pivot dataframe
    """

    df = read_frame(qs)
    df["sample_datetime"] = pd.to_datetime(df["sample_datetime"], errors="coerce")
    df["sample_date"] = df["sample_datetime"].dt.date

    df = df.drop(
        [
            "id",
            "sample_location",
            "sample_sublocation",
            "sample_datetime",
            "sample_comments",
            "is_used",
            "processing_datetime",
            "frozen_datetime",
            "sample_volume",
            "sample_volume_units",
            "freeze_thaw_count",
            "haemolysis_reference",
            "biopsy_location",
            "biopsy_inflamed_status",
            "created",
            "created_by",
            "last_modified",
            "last_modified_by",
        ],
        axis=1,
    )

    df = df.drop_duplicates()

    # Remove all rows where the study_id is not consistent with the studies format
    # Eg negative controls
    match study_name:
        case "mini_music":
            pattern_to_match = r"MINI-\d{3}-\d+"
        case "music":
            pattern_to_match = r"MID-\d{2}-\d+"
        case "gidamps":
            pattern_to_match = r"GID-\d+-."
        case "marvel":
            pattern_to_match = r"^\d{6}$"

    filter = df["study_id"].str.contains(pattern_to_match, regex=True)  # type: ignore
    df = df[filter]

    # Create the pivot table of interest
    output_df = df.pivot_table(
        index=["study_id", "sample_date"],
        columns="sample_type",
        values="sample_id",
        aggfunc=pd.unique,  # type:ignore
        fill_value="None",
    )

    # Sort the output dataframe for mini music and music
    # by center and study id
    match study_name:
        case "gidamps" | "marvel":
            pass

        case "mini_music" | "music":
            sort_music_dataframe(output_df)

    return output_df
