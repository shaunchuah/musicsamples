# Generated by Django 3.2.12 on 2022-02-07 16:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0021_auto_20220202_2030"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalsample",
            name="is_marvel_study",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="sample",
            name="is_marvel_study",
            field=models.BooleanField(default=False),
        ),
    ]
