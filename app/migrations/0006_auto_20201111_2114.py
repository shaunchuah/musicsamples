# Generated by Django 3.1.2 on 2020-11-11 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_auto_20201111_2107"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalsample",
            name="freeze_thaw_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="sample",
            name="freeze_thaw_count",
            field=models.IntegerField(default=0),
        ),
    ]
