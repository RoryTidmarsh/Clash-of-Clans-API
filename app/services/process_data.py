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
    "attack_percentage",
    "defense_stars",
    "defense_percentage",
    "townhallLevel",       # General information about the player
    "attack_th_diff",
    "defense_th_diff",
    "mapPosition",
    "season",              # Other metadata columns
    "battleday",
    "tag",
    "attacker_townhallLevel",
    "defender_townhallLevel",
    "attack_duration",
    "defense_duration",
    "attacker_tag",
    "defender_tag",
    "wartag",
]

def translate_columns(data):
    """
    Replace column names in data with user-friendly names using COLUMN_TRANSLATIONS
    and reorder columns based on COLUMN_ORDER_PRIORITY.

    Args:
        data (list or pandas.DataFrame): A list of dictionaries or a pandas DataFrame.

    Returns:
        list or pandas.DataFrame: Translated data with user-friendly column names,
                                  reordered with COLUMN_ORDER_PRIORITY.
    """

    # Translate and reorder columns for pandas.DataFrame
    if isinstance(data, pd.DataFrame):
        # Rename columns
        data = data.rename(columns=lambda col: COLUMN_TRANSLATIONS.get(col, col))
        # Reorder columns
        ordered_columns = [
            COLUMN_TRANSLATIONS.get(col, col) for col in COLUMN_ORDER_PRIORITY if col in data.columns
        ]
        other_columns = [col for col in data.columns if col not in ordered_columns]
        return data[ordered_columns + other_columns]
    else:
        # Translate and reorder columns for list of dictionaries
        translated_data = []
        for row in data:
            # Translate column names
            translated_row = {COLUMN_TRANSLATIONS.get(key, key): value for key, value in row.items()}
            translated_data.append(translated_row)

        # Reorder columns
        reordered_data = []
        for row in translated_data:
            reordered_row = {key: row[key] for key in COLUMN_ORDER_PRIORITY if key in row}
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