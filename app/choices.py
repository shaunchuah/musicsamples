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
