import pandas as pd

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
        return translated_data


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

if __name__ == "__main__":
    # Example: one Y variable and optional player filter
    drop_stats = {"tag", "attacker_tag", "defender_tag", "wartag", "battleday", "season", "townhallLevel", "opponent_townhallLevel"}

    # Build available_stats from COLUMNTRANSLATIONS excluding drop_stats
    available_stats = [
        {"value": key, "label": (label or key)}
        for key, label in COLUMN_TRANSLATIONS.items()
        if key not in drop_stats
    ]
    print(available_stats)