from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from app.models import BasicScienceBox, ClinicalData, DataStore, ExperimentalID, Sample, StudyIdentifier


@admin.register(StudyIdentifier)
class StudyIdentifierAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "study_name",
        "study_group",
        "study_center",
        "sex",
        "age",
        "genotype_data_available",
        "nod2_mutation_present",
        "il23r_mutation_present",
    ]


@admin.register(ClinicalData)
class ClinicalDataAdmin(admin.ModelAdmin):
    list_display = [
        "study_id",
        "sample_date",
        "music_timepoint",
        "crp",
        "calprotectin",
        "endoscopic_mucosal_healing_at_3_6_months",
        "endoscopic_mucosal_healing_at_12_months",
    ]


@admin.register(Sample)
class SampleAdmin(SimpleHistoryAdmin):
    list_display = [
        "sample_id",
        "study_name",
        "study_id",
        "sample_location",
        "sample_sublocation",
        "sample_comments",
    ]


@admin.register(DataStore)
class DataStoreAdmin(GuardedModelAdmin):
    list_display = [
        "study_name",
        "category",
        "original_file_name",
        "formatted_file_name",
        "size",
        "file_type",
        "upload_finished_at",
        "uploaded_by",
        "comments",
        "music_timepoint",
        "marvel_timepoint",
    ]


@admin.register(BasicScienceBox)
class BasicScienceBoxAdmin(admin.ModelAdmin):
    list_display = [
        "box_id",
        "box_type",
        "basic_science_group",
        "location",
        "species",
        "is_used",
        "created_by",
        "last_modified_by",
    ]


@admin.register(ExperimentalID)
class ExperimentalIDAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "description",
        "get_sample_types",
        "get_tissue_types",
        "created",
        "created_by",
        "last_modified",
        "last_modified_by",
    ]

    @admin.display(description="Sample Types")
    def get_sample_types(self, obj):
        return ", ".join([st.label or st.name for st in obj.sample_types.all()])

    @admin.display(description="Tissue Types")
    def get_tissue_types(self, obj):
        return ", ".join([tt.label or tt.name for tt in obj.tissue_types.all()])
