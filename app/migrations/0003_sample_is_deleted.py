# Generated by Django 3.1.2 on 2020-10-26 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20201022_2354'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
