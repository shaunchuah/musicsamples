# Generated by Django 5.0.6 on 2024-07-21 13:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0028_populate_is_used_from_is_fully_used_and_is_deleted"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalsample",
            name="is_fully_used",
        ),
        migrations.RemoveField(
            model_name="sample",
            name="is_fully_used",
        ),
    ]
