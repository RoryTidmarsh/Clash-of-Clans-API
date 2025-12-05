import pandas as pd
import numpy as np
# Universal dictionary for column translations with user-friendly names and emojis
COLUMN_TRANSLATIONS = {
    "tag": "🏷️ Tag",
    "name": "👤 Player",
    "townhallLevel": "🏰 Townhall Level",
    "mapPosition": "🗺️ Map Position",
    "attacker_townhallLevel": "⚔️ Att TH Level",
    "defender_townhallLevel": "🛡️ Def TH Level",
    "attack_th_diff": "⚔️ Att TH Diff",
    "defense_th_diff": "🛡️ Def TH Diff",
    "attack_stars": "⭐ Att Stars",
    "attack_percentage": "📊 Att %",
    "attack_duration": "⏱️ Att Duration (s)",
    "defender_tag": "🏷️ Def Tag",
    "defense_stars": "⭐ Def Stars",
    "defense_percentage": "📉 Def %",
    "defense_duration": "⏱️ Def Duration (s)",
    "attacker_tag": "🏷️ Att Tag",
    "season": "📅 Season",
    "battleday": "🔥 Battle Day",
    "wartag": "🏷️ War Tag",
}

# Column order priority - columns will appear in this order if present
COLUMN_ORDER_PRIORITY = [
    "name",                # Player name should always come first
    "attack_stars",        # Key performance metrics should appear early
    "defense_stars",
    "attack_percentage",
    "defense_percentage",
    "attack_th_diff",
    "defense_th_diff",
    "attack_duration",
    "defense_duration",
    "townhallLevel",       # General information about the player
    "mapPosition",
    "season",              # Other metadata columns
    "battleday",
    "tag",
    "attacker_townhallLevel",
    "defender_townhallLevel",
    "attacker_tag",
    "defender_tag",
    "wartag",
]
def check_Pandas(data, stage=""):
    """Check if input is pandas DataFrame else raise TypeError."""
    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"Input data is not a pandas DataFrame. Stage: {stage}, got {type(data).__name__}")
    
def translate_columns(data):
    """
    Translate column names in data using COLUMN_TRANSLATIONS.

    Args:
        data (list or pandas.DataFrame): A list of dictionaries or a pandas DataFrame.

    Returns:
        list or pandas.DataFrame: Data with column names translated.
    """
    if isinstance(data, pd.DataFrame):
        # Translate column names for DataFrame
        translated_columns = {col: COLUMN_TRANSLATIONS.get(col, col) for col in data.columns}
        return data.rename(columns=translated_columns)
    else:
        # Translate column names for list of dictionaries
        translated_data = []
        for row in data:
            translated_row = {COLUMN_TRANSLATIONS.get(key, key): value for key, value in row.items()}
            translated_data.append(translated_row)
        return pd.DataFrame(translated_data)


def reorder_columns(data):
    """
    Reorder columns in data based on COLUMN_ORDER_PRIORITY.

    Args:
        data (list or pandas.DataFrame): A list of dictionaries or a pandas DataFrame.

    Returns:
        list or pandas.DataFrame: Data with columns reordered.
    """
    if isinstance(data, pd.DataFrame):
        # Determine columns in priority order
        ordered_columns = [
            COLUMN_TRANSLATIONS.get(col, col) for col in COLUMN_ORDER_PRIORITY if COLUMN_TRANSLATIONS.get(col, col) in data.columns
        ]
        other_columns = [col for col in data.columns if col not in ordered_columns]
        return data[ordered_columns + other_columns]
    else:
        # Reorder columns for list of dictionaries
        reordered_data = []
        for row in data:
            reordered_row = {col: row[col] for col in COLUMN_ORDER_PRIORITY if col in row}
            # Append remaining columns
            reordered_row.update({key: row[key] for key in row if key not in reordered_row})
            reordered_data.append(reordered_row)
        return reordered_data
    

def remove_columns(data, columns_to_remove):
    """
    Remove specified columns from the data.

    Args:
        data (list or pandas.DataFrame): A list of dictionaries or a pandas DataFrame.
        columns_to_remove (list): List of column names to remove.

    Returns:
        list or pandas.DataFrame: Data with specified columns removed.
    """
    if isinstance(data, pd.DataFrame):
        return data.drop(columns=[col for col in columns_to_remove if col in data.columns])
    else:
        raise NotImplementedError("remove_columns function currently only supports pandas DataFrame input.")
        return [
            {key: value for key, value in row.items() if key not in columns_to_remove}
            for row in data
        ]
    
def get_priority_index(stat):
    """Returns position in COLUMN_ORDER_PRIORITY, or a large number if not found."""
    try:
        return COLUMN_ORDER_PRIORITY.index(stat["value"])
    except ValueError:
        return 999  # Put unknown stats at the end

def Pandas_to_Json(data):
    """Convert pandas DataFrame to JSON-compatible format."""

    if isinstance(data, pd.DataFrame):
        data = data.replace([np.inf, -np.inf], None)
        data = data.where(pd.notna(data), None)
        data_JSON = data.to_dict(orient='records')
        if not isinstance(data_JSON, list):
            raise TypeError(f"Converted data must be a list of dictionaries, got {type(data_JSON).__name__}")
        return data.to_json(orient='records')
    else:
        raise TypeError(f"Input data must be a pandas DataFrame, got {type(data).__name__}")
    
def process_data(data, drop_stats=None):
    """Process data by checking type, removing columns, translating and reordering columns.

    Args:
        data (pandas.DataFrame): Input data as a pandas DataFrame.
        drop_stats (set, optional): Set of column names to drop from the data.

    Returns:
        pandas.DataFrame: Processed data.
    """
    # Initial type check
    check_Pandas(data, stage="received from backend")

    # Remove specified columns if any
    if drop_stats:
        data = remove_columns(data, drop_stats)
        # Check after removing columns
        check_Pandas(data, stage="after removing columns")
    
    # Translate and reorder columns
    data = reorder_columns(data)
    check_Pandas(data, stage="after reordering columns")
    data = translate_columns(data)
    check_Pandas(data, stage="after translating columns")

    return data

if __name__ == "__main__":
    # Example: one Y variable and optional player filter
    drop_stats = {"tag", "attacker_tag", "defender_tag", "wartag", "battleday", "season", "townhallLevel", "opponent_townhallLevel"}

    # Test data
    data = pd.DataFrame({
        "tag": ["#ABC123", None, "#XYZ789", "#DEF456"],
        "name": ["DragonSlayer", "WarriorKing", np.nan, "ClanMaster"],
        "townhallLevel": [14, 13, np.nan, 15],
        "mapPosition": [3, np.nan, 7, 1],
        "attacker_townhallLevel": [14, 13, 12, None],
        "defender_townhallLevel": [13, np.nan, 14, 15],
        "attack_th_diff": [1, 0, -2, -1],
        "defense_th_diff": [-1, 1, np.nan, 0],
        "attack_stars": [3, 2, 1, 3],
        "attack_percentage": [98.5, 87.3, 65.2, 100.0],
        "attack_duration": [185, 203, np.nan, 167],
        "defender_tag": ["#DEF999", "#GHI888", "#JKL777", None],
        "defense_stars": [1, np.nan, 2, 0],
        "defense_percentage": [45.8, 72.1, 88.9, 23.4],
        "defense_duration": [None, 198, 215, 142],
        "attacker_tag": ["#MNO666", "#PQR555", np.nan, "#STU444"],
        "season": ["2024-01", "2024-01", "2024-02", "2024-02"],
        "battleday": [1, 2, 1, 3],
        "wartag": ["#WAR001", "#WAR001", "#WAR002", np.nan]
    })

    import app.services.index_data as ID
    actual_data = ID.get_index_data("conan_1014") # returns dict with recent_stats, all_time_stats, filters
    # print(actual_data)
    recent_stats = actual_data["recent_stats"]
    all_time_stats = actual_data["all_time_stats"] 
    print("\nActual Processed Data from index_data.py:")
    print(all_time_stats)
    assert isinstance(all_time_stats, pd.DataFrame)
    assert isinstance(recent_stats, pd.DataFrame)

    processed_data = process_data(all_time_stats, drop_stats=drop_stats)
    assert isinstance(processed_data, pd.DataFrame)
    print("\nProcessed Data after process_data function:")
    print(processed_data)
    
    # Convert to JSON-compatible format
    json_data = Pandas_to_Json(processed_data)
    print("\nJSON-compatible Data:")
    print(json_data)

    assert isinstance(json_data, str)
