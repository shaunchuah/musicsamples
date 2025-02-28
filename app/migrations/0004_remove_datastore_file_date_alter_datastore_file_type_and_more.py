# Generated by Django 5.1.4 on 2025-02-14 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_datastore_file_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datastore',
            name='file_date',
        ),
        migrations.AlterField(
            model_name='datastore',
            name='file_type',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='datastore',
            name='formatted_file_name',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='datastore',
            name='original_file_name',
            field=models.TextField(blank=True),
        ),
    ]
