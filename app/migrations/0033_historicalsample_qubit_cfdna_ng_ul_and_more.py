# Generated by Django 5.0.6 on 2024-07-24 14:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0032_alter_historicalsample_music_timepoint_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalsample",
            name="qubit_cfdna_ng_ul",
            field=models.DecimalField(
                blank=True, decimal_places=3, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="sample",
            name="qubit_cfdna_ng_ul",
            field=models.DecimalField(
                blank=True, decimal_places=3, max_digits=10, null=True
            ),
        ),
    ]
