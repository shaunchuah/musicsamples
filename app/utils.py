import csv
import datetime

import pandas as pd
from django.db.models import Q, QuerySet
from django.http import HttpResponse
from django_pandas.io import read_frame


def export_csv(queryset, study_name="gtrac"):
    """
    Takes in queryset, returns csv download response
    study_name parameter is optional to control the name of the csv file.
    """
    current_date = datetime.datetime.now().strftime("%d-%b-%Y")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="%s_samples_%s.csv"' % (
        study_name,
        current_date,
    )
    writer = csv.writer(response)
    field_names = [field.name for field in queryset.model._meta.get_fields()]
    writer.writerow(field_names)
    for row in queryset:
        values = []
        for field in field_names:
            value = getattr(row, field)
            if value is None:
                value = ""
            values.append(value)
        writer.writerow(values)
    return response


def queryset_by_study_name(model, study_name):
    """
    Takes the model, pass in the study_name parameter and this will
    return a filtered queryset
    """
    if study_name == "music":
        queryset = model.objects.filter(patient_id__startswith="MID-")
    elif study_name == "gidamps":
        queryset = model.objects.filter(patient_id__startswith="GID-")
    elif study_name == "mini_music":
        queryset = model.objects.filter(patient_id__startswith="MINI-")
    elif study_name == "marvel":
        queryset = model.objects.filter(Q(patient_id__regex=r"^[0-9]{6}$"))
    else:
        queryset = model.objects.all()
    return queryset


def render_dataframe_to_csv_response(df: pd.DataFrame, study_name: str):
    """
    Takes in pandas dataframe and study name and
    returns HttpResponse with csv file
    """
    current_date = datetime.datetime.now().strftime("%d-%b-%Y")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=%s_overview_%s.csv" % (
        study_name,
        current_date,
    )
    df.to_csv(response)
    return response


def retrieve_center_number(row):
    patient_id = row.name[0]
    patient_id = str(patient_id)
    return str.split(patient_id, "-")[1]


def retrieve_patient_number(row):
    patient_id = row.name[0]
    patient_id = str(patient_id)
    return str.split(patient_id, "-")[2]


def sort_music_dataframe(df: pd.DataFrame):
    """
    Takes in music or mini_music dataframes and
    sorts by center and patient_id
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
            "is_deleted",
            "is_fully_used",
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

    # Remove all rows where the patient_id is not consistent with the studies format
    # Eg negative controls
    match study_name:
        case "mini_music":
            pattern_to_match = "MINI-\d{3}-\d+"
        case "music":
            pattern_to_match = "MID-\d{2}-\d+"
        case "gidamps":
            pattern_to_match = "GID-\d+-."
        case "marvel":
            pattern_to_match = "^\d{6}$"

    filter = df["patient_id"].str.contains(pattern_to_match, regex=True)
    df = df[filter]

    # Create the pivot table of interest
    output_df = df.pivot_table(
        index=["patient_id", "sample_date"],
        columns="sample_type",
        values="sample_id",
        aggfunc=pd.unique,
        fill_value="None",
    )

    # Sort the output dataframe for mini music and music
    # by center and patient id
    match study_name:
        case "gidamps" | "marvel":
            pass

        case "mini_music" | "music":
            sort_music_dataframe(output_df)

    return output_df
