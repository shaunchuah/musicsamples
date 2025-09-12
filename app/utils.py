import csv
import dataclasses
import datetime

import pandas as pd
from django.db.models import Q, QuerySet
from django.http import HttpResponse
from django_pandas.io import read_frame


def export_csv(queryset, file_prefix="gtrac", file_name="samples", include_related=True):
    """
    Takes in queryset, returns csv download response
    file_prefix: optional, default is gtrac to control the name of the csv file.
    file_name: optional, default is samples
    include_related: optional, default True. If True, includes foreign key fields

    By default takes in a queryset and returns gtrac_samples_<current_date>.csv
    """
    from django.db.models.fields.related import ForeignKey, OneToOneField

    current_date = datetime.datetime.now().strftime("%d-%b-%Y")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="%s_%s_%s.csv"' % (
        file_prefix,
        file_name,
        current_date,
    )
    writer = csv.writer(response)

    # Get all field names including related fields
    fields = []

    # First add the direct fields
    for field in queryset.model._meta.fields:
        fields.append(field.name)

    # Then add the many-to-many fields
    for field in queryset.model._meta.many_to_many:
        fields.append(field.name)

    # Then add the related fields
    if include_related:
        # List of related fields to exclude
        excluded_related_fields = ["study_id__study_name", "study_id__name"]

        for field in queryset.model._meta.fields:
            if isinstance(field, (ForeignKey, OneToOneField)):
                related_model = field.related_model
                if related_model and not related_model.__name__ == "User":
                    for related_field in related_model._meta.fields:
                        # Skip primary keys of related models
                        if not related_field.primary_key:
                            related_name = f"{field.name}__{related_field.name}"
                            # Skip excluded related fields
                            if related_name not in excluded_related_fields:
                                fields.append(related_name)

    # Write header row
    writer.writerow(fields)

    # Write data rows
    for obj in queryset:
        row_data = []
        for field_name in fields:
            if "__" in field_name:
                # This is a related field
                parts = field_name.split("__")
                value = obj
                for part in parts:
                    if value is None:
                        break
                    try:
                        value = getattr(value, part)
                        # Handle callable attributes (like methods)
                        if callable(value):
                            value = value()
                    except (AttributeError, TypeError):
                        value = None
                        break
            else:
                # This is a direct field
                try:
                    value = getattr(obj, field_name)
                    # Handle many-to-many fields first (before callable check)
                    if hasattr(value, "all"):
                        # This is a many-to-many manager
                        related_objects = list(value.all())
                        if related_objects:
                            # Join the string representations
                            value = ", ".join(str(obj) for obj in related_objects)
                        else:
                            value = ""
                    # Handle callable attributes
                    elif callable(value):
                        value = value()
                except (AttributeError, TypeError):
                    value = None

            # Convert None to empty string for CSV
            if value is None:
                value = ""

            row_data.append(value)

        writer.writerow(row_data)

    return response


def queryset_by_study_name(model, study_name):
    """
    Takes the model, pass in the study_name parameter and this will
    return a filtered queryset
    """
    if study_name == "music":
        queryset = model.objects.filter(study_id__name__startswith="MID-")
    elif study_name == "gidamps":
        queryset = model.objects.filter(study_id__name__startswith="GID-")
    elif study_name == "mini_music":
        queryset = model.objects.filter(study_id__name__startswith="MINI-")
    elif study_name == "marvel":
        queryset = model.objects.filter(Q(study_id__name__regex=r"^[0-9]{6}$"))
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
    df.to_csv(response)  # type:ignore
    return response


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
        aggfunc=pd.unique,
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


def historical_changes(query):
    # Historical changes integrates simple history into the sample detail page
    changes = []
    if query is not None:
        last = query.first()
        for all_changes in range(query.count()):
            new_record, old_record = last, last.prev_record
            if old_record is not None:
                delta = new_record.diff_against(old_record)

                # Prepare a new list for processed changes
                processed_changes = []
                for change in delta.changes:
                    # Copy the change to avoid mutating a frozen instance
                    change_dict = change.__dict__.copy()
                    # Check if the field is 'study_id' (or any other FK field you want to handle)
                    if change.field == "study_id":
                        if change.old is not None:
                            try:
                                from app.models import StudyIdentifier

                                old_instance = StudyIdentifier.objects.get(pk=change.old)
                                change_dict["old"] = str(old_instance)
                            except (StudyIdentifier.DoesNotExist, ValueError):  # type: ignore
                                pass
                        if change.new is not None:
                            try:
                                from app.models import StudyIdentifier

                                new_instance = StudyIdentifier.objects.get(pk=change.new)
                                change_dict["new"] = str(new_instance)
                            except (StudyIdentifier.DoesNotExist, ValueError):  # type: ignore
                                pass
                    # Recreate the change object (assumes it's a dataclass)
                    processed_change = dataclasses.replace(change, **change_dict)
                    processed_changes.append(processed_change)

                # Replace delta.changes with processed_changes
                new_delta = dataclasses.replace(delta, changes=processed_changes)
                changes.append(new_delta)
                last = old_record
        return changes
