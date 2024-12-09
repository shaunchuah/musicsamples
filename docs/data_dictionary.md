# Data Dictionary

This standardized data dictionary is used for datasets within G-Trac. Only the common variables across datasets are standardized as shown below. Each study dataset will also include its own study-specific data fields.

As a standard style guide, all variables in datasets will follow the snake_case naming convention. Every character will only be in lower case and underscores will be used instead of spaces.

|Variable|Type|Values|Comments|
|:----|:----|:----|:----|
|study_id|string| | |
|age|int| | |
|sex|string|`male`, `female`| |
|study_group|string|`cd`, `uc`, `ibdu`, `non_ibd`, `await_dx`, `hc`|cd: Crohn's disease, uc: Ulcerative colitis, ibdu: Inflammatory bowel disease unclassified, hc: healthy controls, non-ibd: other medical diagnosis possible so not entirely healthy, await_dx: awaiting diagnostic confirmation|
|height|int| |height in cm|
|weight|float| |weight in kg|
|bmi|float| |body mass index|
|study_center|string|`edinburgh`, `glasgow`, `dundee`| |
|montreal_cd_location|string|`L1`, `L2`, `L3`|L1: ileal only disease, L2: colonic only, L3: ileocolonic involvement|
|montreal_cd_behaviour|string|`B1`, `B2`, `B3`|L1: non-stricturing, non-penetrating, L2: stricturing disease, L3: penetrating disease|
|montreal_perianal|bool|1 or 0|Perianal disease modifier (+p)|
|montreal_upper_gi|bool|1 or 0|Upper GI disease modifier (+/- L4)|
|montreal_uc_severity|string|`S1`, `S2`, `S3`|S1: Mild activity, S2: Moderate activity, S3: Severe activity (search Montreal UC for full definitions)|
|montreal_uc_extent|string|`E1`, `E2`, `E3`|E1: proctitis only, E2: left-sided disease, E3: extensive|
