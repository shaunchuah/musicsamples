# /Users/chershiongchuah/Developer/musicsamples/core/utils/queries.py
# This module provides queryset filtering utilities based on study names.
# It applies study-specific filters to model querysets for data retrieval.

from django.db.models import Q


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
