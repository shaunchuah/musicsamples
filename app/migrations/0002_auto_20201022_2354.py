# Generated by Django 3.1.2 on 2020-10-22 22:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sample",
            name="musicsampleid",
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name="sample",
            name="patientid",
            field=models.CharField(max_length=200),
        ),
    ]
