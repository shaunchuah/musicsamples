# Generated by Django 3.1.2 on 2020-12-10 11:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0009_auto_20201201_1109"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalsample",
            name="haemolysis_reference",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="sample",
            name="haemolysis_reference",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
