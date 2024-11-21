import datetime

import pandas as pd
from django.http import HttpResponse


def export_json_field(dataset_name, jsonfield):
    """
    Takes in jsonfield from dataset and returns csv download response
    """
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{dataset_name}_{current_date}.csv"'
    df = pd.json_normalize(jsonfield)
    df.to_csv(path_or_buf=response, index=False)

    return response
