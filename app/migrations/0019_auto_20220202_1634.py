# Generated by Django 3.2.12 on 2022-02-02 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_auto_20211013_2355'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sample',
            options={'ordering': ['-created']},
        ),
        migrations.AddField(
            model_name='historicalsample',
            name='frozen_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sample',
            name='frozen_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]