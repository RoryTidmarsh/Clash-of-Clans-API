from dotenv import load_dotenv
import os
import pandas as pd
from supabase_client import supabase,store_battle_tag # Import supabase client to load .env variables
# Load environment variables from .env file
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE__SERVICE_KEY")


# Load the battle_tags.csv file into a DataFrame
filepath = "Pussay_battle_tags.csv"
try:
    df = pd.read_csv(filepath)
    print(df.tail())
except FileNotFoundError:
    raise ValueError(f"Error: '{filepath}' file not found.")


    # Add new season to supabase battle_tags table
for row in df.itertuples():
    if row.wartag != "#0": # Skip empty tags
        print(f"Storing battle tag {row.wartag} for day {row.battleday} of season {row.season} to supabase")
        store_battle_tag(row.battleday, row.wartag, row.season)