# Generated by Django 5.0.8 on 2024-11-18 14:28

import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study_name', models.CharField(choices=[('gidamps', 'GI-DAMPs'), ('music', 'MUSIC'), ('mini_music', 'Mini-MUSIC'), ('marvel', 'MARVEL'), ('mini_marvel', 'Mini-MARVEL'), ('fate_cd', 'FATE-CD'), ('none', 'None')], max_length=200)),
                ('sample_id', models.CharField(max_length=200, unique=True)),
                ('patient_id', models.CharField(max_length=200)),
                ('sample_location', models.CharField(max_length=200)),
                ('sample_sublocation', models.CharField(blank=True, max_length=200, null=True)),
                ('sample_type', models.CharField(choices=[('standard_edta', 'Standard EDTA tube'), ('edta_plasma', 'EDTA plasma child aliquot'), ('cfdna_tube', 'PaxGene cfDNA tube'), ('cfdna_plasma', 'PaxGene cfDNA plasma'), ('cfdna_extracted', 'Extracted cfDNA'), ('paxgene_rna', 'PaxGene RNA tube'), ('rna_plasma', 'PaxGene RNA child aliquot'), ('standard_gel', 'Standard gel tube'), ('serum', 'Serum'), ('biopsy_formalin', 'Formalin biopsy'), ('biopsy_rnalater', 'RNAlater biopsy'), ('paraffin_block', 'Paraffin block'), ('stool_standard', 'Standard stool'), ('stool_calprotectin', 'Calprotectin'), ('stool_qfit', 'qFIT'), ('stool_omnigut', 'OmniGut'), ('stool_supernatant', 'Stool supernatant'), ('saliva', 'Saliva'), ('other', 'Other - please specify in comments')], max_length=200)),
                ('sample_datetime', models.DateTimeField()),
                ('sample_comments', models.TextField(blank=True, null=True)),
                ('is_used', models.BooleanField(default=False)),
                ('music_timepoint', models.CharField(blank=True, choices=[('baseline', 'Baseline'), ('3_months', '3 Months'), ('6_months', '6 Months'), ('9_months', '9 Months'), ('12_months', '12 Months')], max_length=50, null=True)),
                ('marvel_timepoint', models.CharField(blank=True, choices=[('baseline', 'Baseline'), ('12_weeks', '12 weeks'), ('24_weeks', '24 weeks')], max_length=50, null=True)),
                ('processing_datetime', models.DateTimeField(blank=True, null=True)),
                ('frozen_datetime', models.DateTimeField(blank=True, null=True)),
                ('sample_volume', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('sample_volume_units', models.CharField(blank=True, choices=[('ml', 'ml'), ('ul', 'ul')], max_length=30, null=True)),
                ('freeze_thaw_count', models.IntegerField(default=0)),
                ('haemolysis_reference', models.CharField(blank=True, choices=[('0', 'Minimal'), ('20', '20 mg/dL'), ('50', '50 mg/dL'), ('100', '100 mg/dL (unusable)'), ('250', '250 mg/dL (unusable)'), ('500', '500 mg/dL (unsuable)'), ('1000', '1000mg/dL (unusable)')], max_length=200, null=True)),
                ('biopsy_location', models.CharField(blank=True, choices=[('terminal_ileum', 'Terminal ileum'), ('caecum', 'Caecum'), ('ascending', 'Ascending colon'), ('transverse', 'Transverse colon'), ('descending', 'Descending colon'), ('sigmoid', 'Sigmoid colon'), ('rectum', 'Rectum'), ('right_colon', 'Right colon'), ('left_colon', 'Left colon'), ('oesophagus', 'Oesophagus'), ('stomach', 'Stomach'), ('duodenum', 'Duodenum')], max_length=100, null=True)),
                ('biopsy_inflamed_status', models.CharField(blank=True, choices=[('inflamed', 'Inflamed'), ('uninflamed', 'Uninflamed'), ('healthy', 'Healthy')], max_length=100, null=True)),
                ('qubit_cfdna_ng_ul', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('paraffin_block_key', models.CharField(blank=True, max_length=10, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(max_length=200)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('last_modified_by', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='HistoricalSample',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('study_name', models.CharField(choices=[('gidamps', 'GI-DAMPs'), ('music', 'MUSIC'), ('mini_music', 'Mini-MUSIC'), ('marvel', 'MARVEL'), ('mini_marvel', 'Mini-MARVEL'), ('fate_cd', 'FATE-CD'), ('none', 'None')], max_length=200)),
                ('sample_id', models.CharField(db_index=True, max_length=200)),
                ('patient_id', models.CharField(max_length=200)),
                ('sample_location', models.CharField(max_length=200)),
                ('sample_sublocation', models.CharField(blank=True, max_length=200, null=True)),
                ('sample_type', models.CharField(choices=[('standard_edta', 'Standard EDTA tube'), ('edta_plasma', 'EDTA plasma child aliquot'), ('cfdna_tube', 'PaxGene cfDNA tube'), ('cfdna_plasma', 'PaxGene cfDNA plasma'), ('cfdna_extracted', 'Extracted cfDNA'), ('paxgene_rna', 'PaxGene RNA tube'), ('rna_plasma', 'PaxGene RNA child aliquot'), ('standard_gel', 'Standard gel tube'), ('serum', 'Serum'), ('biopsy_formalin', 'Formalin biopsy'), ('biopsy_rnalater', 'RNAlater biopsy'), ('paraffin_block', 'Paraffin block'), ('stool_standard', 'Standard stool'), ('stool_calprotectin', 'Calprotectin'), ('stool_qfit', 'qFIT'), ('stool_omnigut', 'OmniGut'), ('stool_supernatant', 'Stool supernatant'), ('saliva', 'Saliva'), ('other', 'Other - please specify in comments')], max_length=200)),
                ('sample_datetime', models.DateTimeField()),
                ('sample_comments', models.TextField(blank=True, null=True)),
                ('is_used', models.BooleanField(default=False)),
                ('music_timepoint', models.CharField(blank=True, choices=[('baseline', 'Baseline'), ('3_months', '3 Months'), ('6_months', '6 Months'), ('9_months', '9 Months'), ('12_months', '12 Months')], max_length=50, null=True)),
                ('marvel_timepoint', models.CharField(blank=True, choices=[('baseline', 'Baseline'), ('12_weeks', '12 weeks'), ('24_weeks', '24 weeks')], max_length=50, null=True)),
                ('processing_datetime', models.DateTimeField(blank=True, null=True)),
                ('frozen_datetime', models.DateTimeField(blank=True, null=True)),
                ('sample_volume', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('sample_volume_units', models.CharField(blank=True, choices=[('ml', 'ml'), ('ul', 'ul')], max_length=30, null=True)),
                ('freeze_thaw_count', models.IntegerField(default=0)),
                ('haemolysis_reference', models.CharField(blank=True, choices=[('0', 'Minimal'), ('20', '20 mg/dL'), ('50', '50 mg/dL'), ('100', '100 mg/dL (unusable)'), ('250', '250 mg/dL (unusable)'), ('500', '500 mg/dL (unsuable)'), ('1000', '1000mg/dL (unusable)')], max_length=200, null=True)),
                ('biopsy_location', models.CharField(blank=True, choices=[('terminal_ileum', 'Terminal ileum'), ('caecum', 'Caecum'), ('ascending', 'Ascending colon'), ('transverse', 'Transverse colon'), ('descending', 'Descending colon'), ('sigmoid', 'Sigmoid colon'), ('rectum', 'Rectum'), ('right_colon', 'Right colon'), ('left_colon', 'Left colon'), ('oesophagus', 'Oesophagus'), ('stomach', 'Stomach'), ('duodenum', 'Duodenum')], max_length=100, null=True)),
                ('biopsy_inflamed_status', models.CharField(blank=True, choices=[('inflamed', 'Inflamed'), ('uninflamed', 'Uninflamed'), ('healthy', 'Healthy')], max_length=100, null=True)),
                ('qubit_cfdna_ng_ul', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('paraffin_block_key', models.CharField(blank=True, max_length=10, null=True)),
                ('created', models.DateTimeField(blank=True, editable=False)),
                ('created_by', models.CharField(max_length=200)),
                ('last_modified', models.DateTimeField(blank=True, editable=False)),
                ('last_modified_by', models.CharField(max_length=200)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical sample',
                'verbose_name_plural': 'historical samples',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
