import csv
import datetime

from django.http import HttpResponse


def export_csv(queryset, study_name):
    """
    Takes in queryset, returns csv file
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
            # if callable(value):
            #     try:
            #         value = value() or ""
            #     except:
            #         value = "Error retrieving value"
            if value is None:
                value = ""
            values.append(value)
        writer.writerow(values)
    return response
