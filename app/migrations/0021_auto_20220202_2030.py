# Generated by Django 3.2.12 on 2022-02-02 20:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0020_auto_20220202_2022"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="note",
            name="author",
        ),
        migrations.RemoveField(
            model_name="note",
            name="sample_tags",
        ),
        migrations.RemoveField(
            model_name="note",
            name="tags",
        ),
        migrations.DeleteModel(
            name="HistoricalNote",
        ),
        migrations.DeleteModel(
            name="Note",
        ),
    ]
