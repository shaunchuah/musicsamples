# Generated by Django 5.1.4 on 2025-02-25 13:45

from django.db import migrations

def transfer_patient_ids(apps, schema_editor):
    Sample = apps.get_model('app', 'Sample')
    StudyIdentifier = apps.get_model('app', 'StudyIdentifier')
    
    # Transfer each unique patient_id to StudyIdentifier
    for sample in Sample.objects.all():
        study_identifier, created = StudyIdentifier.objects.get_or_create(
            name=sample.patient_id
        )
        sample.study_id = study_identifier
        sample.save()

def reverse_transfer(apps, schema_editor):
    Sample = apps.get_model('app', 'Sample')
    for sample in Sample.objects.all():
        if sample.study_identifier:
            sample.patient_id = sample.study_identifier.name
            sample.save()

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_studyidentifier_remove_datastore_sample_id_and_more'),
    ]

    operations = [
        migrations.RunPython(transfer_patient_ids, reverse_transfer),
    ]
