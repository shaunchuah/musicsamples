# Combined Mini-MUSIC and MUSIC pipeline

```py title="assets/combined_music_mini_music.py"
import pandas as pd
from dagster import AssetExecutionContext, MaterializeResult, asset

from music_dagster.resources import GTracResource


@asset(
    group_name="combined_music_mini_music",
    description="Merges music and mini-music dataframes",
)
def combined_music_mini_music_dataframe(
    context: AssetExecutionContext,
    music_cleaned_dataframe: pd.DataFrame,
    mini_music_cleaned_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    music_df = music_cleaned_dataframe
    mini_music_df = mini_music_cleaned_dataframe

    overlapping_columns = set(music_df.columns).intersection(set(mini_music_df.columns))
    music_only_columns = set(music_df.columns).difference(set(mini_music_df.columns))
    mini_music_only_columns = set(mini_music_df.columns).difference(
        set(music_df.columns)
    )

    df = pd.concat([music_df, mini_music_df])

    context.add_output_metadata(
        {
            "dagster/row_count": df.shape[0],
            "input_music_df_dimension": f"{music_df.shape[0]} rows x {music_df.shape[1]} columns",
            "input_mini_music_df_dimension": f"{mini_music_df.shape[0]} rows x {mini_music_df.shape[1]} columns",
            "output_df_dimension": f"{df.shape[0]} rows x {df.shape[1]} columns",
            "overlapping_column_count": len(overlapping_columns),
            "overlapping_column_list": sorted(list(overlapping_columns)),
            "music_only_columns": sorted(list(music_only_columns)),
            "mini_music_only_columns": sorted(list(mini_music_only_columns)),
        }
    )
    return df


@asset(
    group_name="combined_music_mini_music",
    description="Stores combined dataframe in G-Trac",
)
def store_combined_music_in_gtrac(
    combined_music_mini_music_dataframe: pd.DataFrame, gtrac: GTracResource
) -> MaterializeResult:
    df = combined_music_mini_music_dataframe
    json = df.to_json(orient="records")
    data = {
        "study_name": "music",
        "name": "combined_music",
        "description": (
            "Combined music and mini-music dataframes. "
            "Consider dropping timepoint_4 and timepoint_5 to harmonize "
            "the longitudinal timepoints between both studies. "
            "Demographic data can be generated from timepoint_1 rows."
        ),
        "json": json,
    }
    response = gtrac.submit_data(data)
    return MaterializeResult(
        metadata={
            "status_code": str(response.status_code),
        }
    )
```
