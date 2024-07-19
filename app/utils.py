import csv
import datetime

from django.db.models import Q
from django.http import HttpResponse


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
    elif study_name == "minimusic":
        queryset = model.objects.filter(patient_id__startswith="MINI-")
    elif study_name == "marvel":
        queryset = model.objects.filter(
            Q(patient_id__regex=r"^[0-9]{6}$") | Q(is_marvel_study=True)
        )
    else:
        queryset = model.objects.all()
    return queryset
