# /Users/chershiongchuah/Developer/musicsamples/core/utils/export.py
# This module provides CSV export and dataframe rendering utilities.
# It generates downloadable CSV responses from querysets and dataframes.

import csv
import datetime

import pandas as pd
from django.http import HttpResponse


def export_csv(queryset, file_prefix="gtrac", file_name="samples", include_related=True):
    """
    Takes in queryset, returns csv download response
    file_prefix: optional, default is gtrac to control the name of the csv file.
    file_name: optional, default is samples
    include_related: optional, default True. If True, includes foreign key fields

    By default takes in a queryset and returns gtrac_samples_[current_date].csv
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

    # Custom derived fields for specific models
    if queryset.model.__name__ == "BasicScienceBox":
        fields.extend(["sample_type_labels_display", "tissue_type_labels_display", "basic_science_groups_display"])
    elif queryset.model.__name__ == "Experiment":
        fields.append("boxes")

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

    # Move specific fields to the end
    special_fields = ["created", "created_by", "last_modified", "last_modified_by"]
    regular_fields = [f for f in fields if f not in special_fields]
    special_fields_present = [f for f in special_fields if f in fields]
    fields = regular_fields + special_fields_present

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
