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
    PARAFFIN_BLOCK = "paraffin_block", "Paraffin block"
    STOOL_STANDARD = "stool_standard", "Standard stool"
    STOOL_CALPROTECTIN = "stool_calprotectin", "Calprotectin"
    STOOL_QFIT = "stool_qfit", "qFIT"
    STOOL_OMNIGUT = "stool_omnigut", "OmniGut"
    STOOL_SUPERNATANT = "stool_supernatant", "Stool supernatant"
    SALIVA = "saliva", "Saliva"
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
    FATE_CD = "fate_cd", "FATE-CD"
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


class FileCategoryChoices(models.TextChoices):
    UNCATEGORISED = "uncategorised", "Uncategorised"
    ENDOSCOPY_VIDEOS = "endoscopy_videos", "Endoscopy Videos"
    HISTOLOGY_SLIDES = "histology_slides", "Histology Slides"
    FAPI_PET_MRI = "fapi_pet_mri", "FAPI PET MRI"
    SPATIAL_TRANSCRIPTOMICS = "spatial_transcriptomics", "Spatial Transcriptomics"


class StudyCenterChoices(models.TextChoices):
    EDINBURGH = "edinburgh", "Edinburgh"
    GLASGOW = "glasgow", "Glasgow"
    DUNDEE = "dundee", "Dundee"
    ABERDEEN = "aberdeen", "Aberdeen"


class StudyGroupChoices(models.TextChoices):
    UC = "uc", "UC"
    CD = "cd", "CD"
    HC = "hc", "HC"
    IBDU = "ibdu", "IBDU"
    NON_IBD = "non_ibd", "Non-IBD"
    AWAIT_DX = "await_dx", "Awaiting Diagnosis"
    OTHER = "other", "Other"


class SexChoices(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"


class BasicScienceGroupChoices(models.TextChoices):
    BAIN = "bain", "Bain"
    JONES = "jones", "Jones"
    HO = "ho", "Ho"
    OTHER = "other", "Other"


class BasicScienceBoxTypeChoices(models.TextChoices):
    BASIC_SCIENCE_SAMPLES = "basic_science_samples", "Samples"
    BASIC_SCIENCE_REAGENTS = "basic_science_reagents", "Reagents"


class BasicScienceSampleTypeChoices(models.TextChoices):
    RNA = "rna", "RNA"
    DNA = "dna", "DNA"
    TISSUE = "tissue", "Tissue"
    CELLS = "cells", "Cells"
    SUPERNATANTS = "supernatants", "Supernatants"
    OCT_COMPOUND = "oct_compound", "OCT Compound"
    OTHER = "other", "Other"


class TissueTypeChoices(models.TextChoices):
    BLOOD = "blood", "Blood"
    GUT = "gut", "Gut"
    STOOL = "stool", "Stool"
    BONE_MARROW = "bone_marrow", "Bone Marrow"
    LUNG = "lung", "Lung"
    BRONCHOALVEOLAR_LAVAGE = "bronchoalveolar_lavage", "Bronchoalveolar Lavage"
    OTHER = "other", "Other"


class SpeciesChoices(models.TextChoices):
    HUMAN = "human", "Human"
    MOUSE = "mouse", "Mouse"


class FreezerLocationChoices(models.TextChoices):
    SII_FREEZER_1 = "sii_freezer_1", "SII Freezer 1"


class RowChoices(models.TextChoices):
    A = "A", "A"
    B = "B", "B"
    C = "C", "C"
    D = "D", "D"
    E = "E", "E"
    F = "F", "F"
    G = "G", "G"
    H = "H", "H"
    I = "I", "I"  # noqa: E741
    J = "J", "J"
    K = "K", "K"
    L = "L", "L"
    M = "M", "M"
    N = "N", "N"
    O = "O", "O"  # noqa: E741
    P = "P", "P"
    Q = "Q", "Q"
    R = "R", "R"
    S = "S", "S"
    T = "T", "T"
    U = "U", "U"
    V = "V", "V"
    W = "W", "W"
    X = "X", "X"
    Y = "Y", "Y"
    Z = "Z", "Z"


class ColumnChoices(models.TextChoices):
    ONE = "1", "1"
    TWO = "2", "2"
    THREE = "3", "3"
    FOUR = "4", "4"
    FIVE = "5", "5"
    SIX = "6", "6"
    SEVEN = "7", "7"
    EIGHT = "8", "8"


class DepthChoices(models.TextChoices):
    A = "A", "A"
    B = "B", "B"
    C = "C", "C"
    D = "D", "D"
