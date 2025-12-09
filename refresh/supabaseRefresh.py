"""The supabase client module for refreshing data, including functions to store and retrieve battle tags and war status.
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env.refresh'))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def store_battle_tag(battleday, wartag, season):
    data = {
        "battleday": battleday,
        "wartag": wartag,
        "season": season
    }
    response = supabase.table("battle_tags").insert(data).execute()
    return response.data