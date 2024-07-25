from django.db import models

SAMPLE_TYPE_CHOICES = (
    ("", "Select type"),
    (
        "Standard EDTA tube",
        (
            ("Standard EDTA tube", "Standard EDTA tube"),
            ("EDTA plasma child aliquot", "EDTA plasma child aliquot"),
        ),
    ),
    (
        "PaxGene ccfDNA tube",
        (
            ("PaxGene ccfDNA tube", "PaxGene ccfDNA tube"),
            (
                "PaxGene ccfDNA plasma child aliquot",
                "PaxGene ccfDNA plasma child aliquot",
            ),
            (
                "PaxGene ccfDNA extracted cfDNA",
                "PaxGene ccfDNA extracted cfDNA",
            ),
        ),
    ),
    (
        "PaxGene RNA tube",
        (
            ("PaxGene RNA tube", "PaxGene RNA tube"),
            ("PaxGene RNA child aliquot", "PaxGene RNA child aliquot"),
        ),
    ),
    (
        "Standard Gel/Serum tube",
        (
            ("Standard gel tube", "Standard gel tube"),
            ("Serum child aliquot", "Serum child aliquot"),
        ),
    ),
    (
        "Tissue/Biopsy",
        (
            ("Formalin biopsy", "Formalin biopsy"),
            ("RNAlater biopsy", "RNAlater biopsy"),
            ("Paraffin tissue block", "Paraffin tissue block"),
        ),
    ),
    (
        "Stool",
        (
            ("Standard stool container", "Standard stool container"),
            ("Calprotectin", "Calprotectin"),
            ("FIT", "FIT"),
            ("OmniGut", "Omnigut"),
            ("Stool supernatant", "Stool supernatant"),
        ),
    ),
    ("Saliva", (("Saliva", "Saliva"),)),
    ("Other", (("Other", "Other please specify in comments"),)),
)

HAEMOLYSIS_REFERENCE_CHOICES = (
    ("", "Select category"),
    ("0", "Minimal"),
    ("20", "20 mg/dL"),
    ("50", "50 mg/dL"),
    ("100", "100 mg/dL (unusable)"),
    ("250", "250 mg/dL (unusable)"),
    ("500", "500 mg/dL (unusable)"),
    ("1000", "1000 mg/dL (unusable)"),
)

BIOPSY_LOCATION_CHOICES = (
    ("", "Select biopsy location"),
    ("Terminal ileum", "Terminal ileum"),
    ("Caecum", "Caecum"),
    ("Ascending colon", "Ascending colon"),
    ("Transverse colon", "Transverse colon"),
    ("Descending colon", "Descending colon"),
    ("Sigmoid colon", "Sigmoid colon"),
    ("Rectum", "Rectum"),
    ("Right colon", "Right colon"),
    ("Left colon", "Left colon"),
    ("Oesophagus", "Oesophagus"),
    ("Stomach", "Stomach"),
    ("Duodenum", "Duodenum"),
)

BIOPSY_INFLAMED_STATUS_CHOICES = (
    ("", "Select inflamed status"),
    ("inflamed", "Inflamed"),
    ("uninflamed", "Uninflamed"),
    ("healthy", "Healthy"),
)

SAMPLE_VOLUME_UNIT_CHOICES = (
    ("", "Select unit"),
    ("ml", "ml"),
    ("ul", "ul"),
)


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
