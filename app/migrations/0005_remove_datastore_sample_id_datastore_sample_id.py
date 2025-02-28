# Generated by Django 5.1.4 on 2025-02-14 15:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_remove_datastore_file_date_alter_datastore_file_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datastore',
            name='sample_id',
        ),
        migrations.AddField(
            model_name='datastore',
            name='sample_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='app.sample'),
        ),
    ]
