# Generated by Django 5.0.8 on 2024-11-21 15:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='csv',
        ),
    ]
