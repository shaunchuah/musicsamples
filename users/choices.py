from django.db import models


class JobTitleChoices(models.TextChoices):
    RESEARCH_ASSISTANT = "research_assistant", "Research Assistant"
    POSTDOCTORAL_RESEARCHER = "postdoctoral_researcher", "Postdoctoral Researcher"
    PHD_STUDENT = "phd_student", "PhD Student"
    CLINICAL_RESEARCH_FELLOW = "clinical_research_fellow", "Clinical Research Fellow"
    CLINICAL_RESEARCH_NURSE = "clinical_research_nurse", "Clinical Research Nurse"
    CLINICIAN_SCIENTIST = "clinician_scientist", "Clinician Scientist"
    SCIENTIST = "scientist", "Scientist"
    UNKNOWN = "unknown", "Unknown"


class PrimaryOrganisationChoices(models.TextChoices):
    NHS_LOTHIAN = "nhs_lothian", "NHS Lothian"
    NHS_GGC = "nhs_ggc", "NHS GGC"
    NHS_TAYSIDE = "nhs_tayside", "NHS Tayside"
    UNIVERSITY_OF_EDINBURGH = "university_of_edinburgh", "University of Edinburgh"
    UNIVERSITY_OF_GLASGOW = "university_of_glasgow", "University of Glasgow"
    UNIVERSITY_OF_DUNDEE = "university_of_dundee", "University of Dundee"
    UNKNOWN = "unknown", "Unknown"
