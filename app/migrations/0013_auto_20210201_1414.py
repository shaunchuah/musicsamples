# Generated by Django 3.1.2 on 2021-02-01 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20210201_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalnote',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='note',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]