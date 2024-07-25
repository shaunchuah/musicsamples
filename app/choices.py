from django.db import models


class SampleTypeChoices(models.TextChoices):
    STANDARD_EDTA = "standard_edta", "Standard EDTA tube"
    EDTA_PLASMA = "edta_plasma", "EDTA plasma child aliquot"
    CFDNA_TUBE = "cfdna_tube", "PaxGene cfDNA tube"
    CFDNA_PLASMA = "cfdna_plasma", "PaxGene cfDNA plasma"
    CFDNA_EXTRACTED = "cfdna_extracted", "Extracted cfDNA"
    PAXGENE_RNA = "paxgene_rna", "PaxGene RNA tube"
    PAXGENE_RNA_PLASMA = "rna_plasma", "PaxGene RNA child aliquot"
    STANDARD_GEL = "standard_gel", "Standard gel tube"
    SERUM = "serum", "Serum"
    BIOPSY_FORMALIN = "biopsy_formalin", "Formalin biopsy"
    BIOPSY_RNALATER = "biopsy_rnalater", "RNAlater biopsy"
    STOOL_STANDARD = "stool_standard", "Standard stool"
    STOOL_CALPROTECTIN = "stool_calprotectin", "Calprotectin"
    STOOL_QFIT = "stool_qfit", "qFIT"
    STOOL_OMNIGUT = "stool_omnigut", "OmniGut"
    STOOL_SUPERNATANT = "stool_supernatant", "Stool supernatant"
    SALIVA = "saliva", "Saliva"
    PARAFFIN_BLOCK = "paraffin_block", "Paraffin block"
    OTHER = "other", "Other - please specify in comments"


class BiopsyLocationChoices(models.TextChoices):
    TERMINAL_ILEUM = "terminal_ileum", "Terminal ileum"
    CAECUM = "caecum", "Caecum"
    ASCENDING = "ascending", "Ascending colon"
    TRANSVERSE = "transverse", "Transverse colon"
    DESCENDING = "descending", "Descending colon"
    SIGMOID = "sigmoid", "Sigmoid colon"
    RECTUM = "rectum", "Rectum"
    RIGHT_COLON = "right_colon", "Right colon"
    LEFT_COLON = "left_colon", "Left colon"
    OESOPHAGUS = "oesophagus", "Oesophagus"
    STOMACH = "stomach", "Stomach"
    DUODENUM = "duodenum", "Duodenum"


class SampleVolumeUnitChoices(models.TextChoices):
    ML = "ml", "ml"
    UL = "ul", "ul"


class BiopsyInflamedStatusChoices(models.TextChoices):
    INFLAMED = "inflamed", "Inflamed"
    UNINFLAMED = "uninflamed", "Uninflamed"
    HEALTHY = "healthy", "Healthy"


class HaemolysisReferenceChoices(models.TextChoices):
    ZERO = "0", "Minimal"
    TWENTY = "20", "20 mg/dL"
    FIFTY = "50", "50 mg/dL"
    ONE_HUNDRED = "100", "100 mg/dL (unusable)"
    TWO_FIFTY = "250", "250 mg/dL (unusable)"
    FIVE_HUNDRED = "500", "500 mg/dL (unsuable)"
    ONE_THOUSAND = "1000", "1000mg/dL (unusable)"


class StudyNameChoices(models.TextChoices):
    GIDAMPS = "gidamps", "GI-DAMPs"
    MUSIC = "music", "MUSIC"
    MINI_MUSIC = "mini_music", "Mini-MUSIC"
    MARVEL = "marvel", "MARVEL"
    MINI_MARVEL = "mini_marvel", "Mini-MARVEL"
    NONE = "none", "None"


class MusicTimepointChoices(models.TextChoices):
    BASELINE = "baseline", "Baseline"
    THREE_MONTHS = "3_months", "3 Months"
    SIX_MONTHS = "6_months", "6 Months"
    NINE_MONTHS = "9_months", "9 Months"
    TWELVE_MONTHS = "12_months", "12 Months"


class MarvelTimepointChoices(models.TextChoices):
    BASELINE = "baseline", "Baseline"
    TWELVE_WEEKS = "12_weeks", "12 weeks"
    TWENTY_FOUR_WEEKS = "24_weeks", "24 weeks"
