# Generated by Django 5.1.4 on 2025-02-25 15:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_studyidentifier_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datastore',
            name='patient_id',
        ),
        migrations.AddField(
            model_name='datastore',
            name='study_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='files', to='app.studyidentifier'),
        ),
    ]
