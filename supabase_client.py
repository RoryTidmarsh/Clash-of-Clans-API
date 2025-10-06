from supabase import create_client
import os
from dotenv import load_dotenv
import numpy as np
from typing import Iterable

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def store_battle_tag(battleday, wartag, season):
    data = {
        "battleday": battleday,
        "wartag": wartag,
        "season": season
    }
    supabase.table("battle_tags").insert(data).execute()


def get_battle_tags(SQL_query=None):
    response = supabase.table("battle_tags").select(SQL_query).execute()
    return response.data

def store_war_status(wartag, coc_war_status, loading_status, last_updated, data_file=""):
    data = {
        "wartag": wartag,
        "coc_war_status": coc_war_status,
        "loading_status": loading_status,
        "last_updated": last_updated,
        "data_file": data_file
    }
    supabase.table("war_status").insert(data).execute()

def get_war_status(SQL_query=None):
    response = supabase.table("war_status").select(SQL_query).execute()
    return response.data

def store_war_data(dataframe_row):
    if not isinstance(dataframe_row, dict):
        data = dataframe_row.to_dict()
    else:
        data = dataframe_row

    # Define required columns for war_data table (keep in sync with CSV/DataFrame layout)
    REQUIRED_WAR_COLUMNS = [
        'tag','name','townhallLevel','mapPosition','attacker_townhallLevel','defender_townhallLevel',
        'attack_th_diff','defense_th_diff','attack_stars','attack_percentage','attack_duration','defender_tag',
        'defense_stars','defense_percentage','defense_duration','attacker_tag','season','battleday','wartag'
    ]

    def _check_and_fill_columns(d: dict, required: Iterable[str], context: str = "war_data") -> dict:
        """Ensure all required columns exist in dict `d`.

        Missing columns are added with None (safe for JSON/SQL null). A print statement
        alerts which columns were missing and were added.
        """
        missing = [c for c in required if c not in d]
        if missing:
            print(f"[supabase_client] Warning: missing columns for {context}: {missing}. Filling with nulls.")
            for c in missing:
                # Use None (serialized to JSON null). np.nan is not JSON serializable.
                d[c] = None
        return d

    # Apply column check/fill. Use wartag for context if present.
    context = data.get('wartag') if isinstance(data, dict) else 'war_data'
    data = _check_and_fill_columns(dict(data), REQUIRED_WAR_COLUMNS, context=context)

    supabase.table("war_data").insert(data).execute()
    # def update_war_status(record_id, updates):
#     supabase.table("war_status").update(updates).eq("id", record_id).execute()