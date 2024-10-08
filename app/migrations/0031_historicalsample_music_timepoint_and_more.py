# Generated by Django 5.0.6 on 2024-07-24 10:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0030_remove_historicalsample_is_deleted_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalsample",
            name="music_timepoint",
            field=models.CharField(
                choices=[
                    ("baseline", "Baseline"),
                    ("3_months", "3 Months"),
                    ("6_months", "6 Months"),
                    ("9_months", "9 Months"),
                    ("12_months", "12 Months"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="sample",
            name="music_timepoint",
            field=models.CharField(
                choices=[
                    ("baseline", "Baseline"),
                    ("3_months", "3 Months"),
                    ("6_months", "6 Months"),
                    ("9_months", "9 Months"),
                    ("12_months", "12 Months"),
                ],
                max_length=50,
                null=True,
            ),
        ),
    ]
