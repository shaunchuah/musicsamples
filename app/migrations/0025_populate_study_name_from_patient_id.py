# Generated by Django 5.0.6 on 2024-07-19 19:06
import re

from django.db import migrations

from app.choices import StudyNameChoices


def retrieve_study_name_from_patient_id(patient_id):
    """
    Pass in the patient ID string and outputs the appropriate study name
    """
    if patient_id[0:4] == "MID-":
        return StudyNameChoices.MUSIC
    elif patient_id[0:4] == "GID-":
        return StudyNameChoices.GIDAMPS
    elif patient_id[0:4] == "MINI":
        return StudyNameChoices.MINI_MUSIC
    elif bool(re.match(r"^\d{6}$", patient_id)):
        return StudyNameChoices.MARVEL
    else:
        return StudyNameChoices.NONE


def forwards(apps, _):
    Sample = apps.get_model("app", "Sample")
    samples = Sample.objects.all()
    for sample in samples:
        sample.study_name = retrieve_study_name_from_patient_id(sample.patient_id)
        sample.save()

    HistoricalSample = apps.get_model("app", "HistoricalSample")
    historical_samples = HistoricalSample.objects.all()
    for historical_sample in historical_samples:
        historical_sample.study_name = retrieve_study_name_from_patient_id(
            historical_sample.patient_id
        )
        historical_sample.save()


def backwards(apps, _):
    Sample = apps.get_model("app", "Sample")
    samples = Sample.objects.all()
    for sample in samples:
        sample.study_name = StudyNameChoices.NONE
        sample.save()

    HistoricalSample = apps.get_model("app", "HistoricalSample")
    historical_samples = HistoricalSample.objects.all()
    for historical_sample in historical_samples:
        historical_sample.study_name = StudyNameChoices.NONE
        historical_sample.save()


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0024_historicalsample_study_name_sample_study_name"),
    ]

    operations = [migrations.RunPython(forwards, backwards)]