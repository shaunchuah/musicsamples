# Data Issues

Here is a list of data issues to be aware about:

## Disease activity definitions vary between studies

The `disease_activity` and `physician_global_assessment` variables differ between GI-DAMPs, MUSIC, and Mini-MUSIC.

### Current Variations in Disease Activity Classifications by Study

| Study      | Field Name | Categories |
|------------|------------|------------|
| GI-DAMPs   | ibd_status | - Biochemical remission (normal CRP AND FC< 250)<br>- Remission<br>- Active<br>- Highly active (admission for IV steroids)<br>- Not applicable |
| MUSIC      | physician_global_assessment | - Remission<br>- Mildly active<br>- Moderately active<br>- Severely active |
|           | disease_activity | - Biochemical remission<br>- Remission<br>- Active<br>- Biochemically Active<br>- Not applicable |
| Mini-MUSIC | physician_global_assessment | - Biochemical remission<br>- Clinical remission<br>- Mildly active<br>- Moderately active<br>- Severely active |
|           | disease_activity | - Remission<br>- Mild<br>- Moderate<br>- Severe<br>- Not applicable |

### Potential Standardized Definition

Disease activity could be standardised using these common variables:

- `has_active_symptoms` (Boolean)
- `crp` (mg/L, threshold > 5)
- `calprotectin` (μg/g, threshold > 250)

#### Example Implementation Logic

```python
def calculate_disease_activity(row):
    """
    Returns: 'biochem_active' if has_active_symptoms and CRP > 5 and calprotectin > 250, 
            'active' if has_active_symptoms but CRP or calprotectin do not meet above threshold,
            'remission' if not has_active_symptoms but CRP > 5 or calprotectin > 250,
            'biochem_remission' if not has_active_symptoms and CRP < 5 and calprotectin < 250.
    """
    has_active_symptoms = row['has_active_symptoms']
    crp = row['crp']
    calprotectin = row['calprotectin']
    
    if has_active_symptoms:
        if crp > 5 and calprotectin > 250:
            return 'biochem_active'
        else:
            return 'active'
    else:
        if crp > 5 or calprotectin > 250:
            return 'remission'
        else:
            return 'biochem_remission'
```


#### Example Usage with DataFrame

```py
import pandas as pd

data = {
    'has_active_symptoms': [True, False, True, False],
    'crp': [6.2, 2.1, 7.8, 1.5],
    'calprotectin': [300, 150, 180, 100]
}
df = pd.DataFrame(data)

# Apply function to DataFrame
df['standardised_disease_activity'] = df.apply(calculate_disease_activity, axis=1)
print(df)
           
```

## GI-DAMPs Study ID Format Evolution

### Historical Format

- Initial format: `GID-xxx-P` or `GID-xxx-HC`
  - xxx: integer with inconsistent leading zeros (e.g., `GID-001-P` vs `GID-1-P`)
  - P: Patient, HC: Healthy Control

### Multi-Center Expansion

- Center-specific formats introduced:
  - Edinburgh: `GID-x`
  - Glasgow: `GID-136-x`
  - Dundee: `GID-138-x`
  
### Known Issues

1. Potential conflicts with Edinburgh legacy IDs `GID-136-P` and `GID-138-P`
2. Inconsistent formats at Glasgow/Dundee sites (e.g., `GID-136-x-P`)

### Current Standard (December 2024)

- Remove `-P` and `-HC` suffixes (use `study_group` column instead)
- Use `GID-` prefix only
- No leading zeros
- Center-specific formats:
  - Edinburgh: `GID-x`
  - Glasgow: `GID-136-x`
  - Dundee: `GID-138-x`

⚠️ **Important**: When merging GI-DAMPs data, carefully check `study_id` column for legacy formats.
