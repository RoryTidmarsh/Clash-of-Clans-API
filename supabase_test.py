from dotenv import load_dotenv
import os
import pandas as pd
from supabase_client import supabase,store_battle_tag, store_war_status # Import supabase client to load .env variables
# Load environment variables from .env file
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

def battle_tags_to_supabase(filepath = "Pussay_battle_tags.csv"):
    # Load the battle_tags.csv file into a DataFrame
    try:
        df = pd.read_csv(filepath)
        print(df.tail())
    except FileNotFoundError:
        raise ValueError(f"Error: '{filepath}' file not found.")


    for row in df.itertuples():
        if row.wartag != "#0": # Skip empty tags
            # Check if the battle tag already exists in the database for any day or season
            existing_tags = supabase.table("battle_tags").select("*").eq("wartag", row.wartag).execute()
            if existing_tags.data:
                print(f"Battle tag {row.wartag} already exists in the database. Skipping insertion.")
            else:
                print(f"Storing battle tag {row.wartag} for day {row.battleday} of season {row.season} to supabase")
                store_battle_tag(row.battleday, row.wartag, row.season)


def war_status_to_supabase(filepath = "war_status.csv"):
    # Load the war_status.csv file into a DataFrame
    try:
        df = pd.read_csv(filepath)
        print(df.tail())
    except FileNotFoundError:
        raise ValueError(f"Error: '{filepath}' file not found.")

    for row in df.itertuples():
        if row.wartag != "#0": # Skip empty tags
            # Check if the battle tag already exists in the database for any day or season and access the COC_war_status and loading_status columns
            existing_status = supabase.table("war_status").select("*").eq("wartag", row.wartag).execute()
            if existing_status.data:
                print(f"War status for battle tag {row.wartag} already exists in the database. Skipping insertion.")
                useful_info_row = {'wartag': row.wartag, 'coc_war_status': row.COC_war_status, 'loading_status': row.loading_status, 'last_updated': row.last_updated}
                print(useful_info_row)

            else:
                print(f"Storing war status for battle tag {row.wartag} to supabase")
                store_war_status(row.wartag, row.COC_war_status, row.loading_status, row.last_updated)
                
if __name__ == "__main__":
    
    # battle_tags_to_supabase()  # Call the function with the default filepath
    war_status_to_supabase()  # Call the function with the default filepath
    