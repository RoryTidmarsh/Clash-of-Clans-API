import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
import os
from app.supabase_client import supabase,store_battle_tag # Import supabase client to load .env variables
# Load environment variables from .env file
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
coc_api_key = os.getenv("COC_API_KEY")


# Pussay Clan Tag
clan_tag = "%23CQGY2LQU"
clan_name = "Pussay Palace"
base_url = "https://api.clashofclans.com/v1"
url = base_url + f"/clans/{clan_tag}"
headers = {
    "Accept": "application/json",
    "authorization": "Bearer %s" % coc_api_key,
}
debug_print_statements = False
# Make the request to the API
# response = requests.request("GET", url, headers=headers)
# data = response.json()
# print(data.keys())
# Find rozzledog72 in the member list and print their tag and role
# for member in data["memberList"]:
#     if member["name"] == "rozzledog 72":
#         print("Name:", member["name"])
#         print("Role:", member["role"])
#         print("Trophies:", member["trophies"])
#         print("TH level:",member["townHallLevel"])


# Accessing clan war log
# response_warlog = requests.request("GET", url + "/warlog", headers=headers)
# data_warlog = response_warlog.json()
# print("War log keys: ", data_warlog["items"][0].keys()) # Keys: ['result', 'endTime', 'teamSize', 'attacksPerMember', 'battleModifier', 'clan', 'opponent']

# Response codes from the API
response_codes = {
    200: "Success",
    400: "Client provided incorrect parameters for the request.",
    403: "Access denied, either because of missing/incorrect credentials or used API token does not grant access to the requested resource. Check the Api Key.",
    404: "The requested resource does not exist.",
    429: "Too many requests. You are rate limited. Wait before sending more requests.",
    500: "Server error. Something is wrong on Clash of Clans side.",
    503: "Server is down for maintenance.",
}

def get_war_tags(clan_tag, headers = headers):
    """Get the war tags for the current war league of the clan.

    Args:
        clan_tag (str): The clan tag of the clan to get the war league information for.
        headers (dict): The headers to use for the API request.
    Returns:
        dict: The current war league information for the clan.
    """
    # Accessing CWL information
    leaguegroup_url = f"{base_url}/clans/{clan_tag}/currentwar/leaguegroup"
    leaguegroup_response = requests.get(leaguegroup_url, headers=headers)
    print("League group response status code:", leaguegroup_response.status_code)

    # Check for errors in the response and print
    if leaguegroup_response.status_code != 200:
        print("Error: ", response_codes[leaguegroup_response.status_code])
        exit()

    # Get the JSON data from the response
    leaguegroup_data = leaguegroup_response.json()  # Keys: ['state', 'season', 'clans', 'rounds'])
    season = leaguegroup_data["season"]

    # Create a DataFrame to store battle tags in
    battle_tag_df = pd.DataFrame(columns=["battleday", "wartag1", "wartag2", "wartag3", "wartag4", "season"])

    # Tags each war in the league group
    cwl_war_tags = leaguegroup_data["rounds"]
    for i,battleday_tags in enumerate(cwl_war_tags):
        battleday_tags = battleday_tags["warTags"]
        battle_tag_df.loc[i] = [i+1, battleday_tags[0], battleday_tags[1], battleday_tags[2], battleday_tags[3], season]

    # Find how many rows empty tags there are "#0"
    empty_tags = battle_tag_df["wartag1"].value_counts().get("#0", 0)
    if empty_tags > 0:
        print(f"Found {empty_tags} empty days in the war tag DataFrame.")
    return battle_tag_df, season

def append_days_to_dataframe(existing_data, new_df, season):
    """Append new battleday data to the existing DataFrame for the current season.

    Args:
        existing_data (pd.DataFrame): existing DataFrame containing battle tags from previous seasons and the current season (if any)
        new_df (pd.DataFrame): DataFrame containing new battle tags for the current season
        season (str): string of the season to append data for

    Returns:
        pd.DataFrame: DataFrame with the new battleday data appended
    """
    # Check that there is only 1 season in the new_df
    unique_seasons = new_df["season"].unique()
    if len(unique_seasons) != 1:
        raise ValueError(f'More than 1 season in the new data. Found seasons: {unique_seasons}')
    
    new_season = unique_seasons[0]
    
    # Verify the season matches the input parameter
    if new_season != season:
        raise ValueError(f'Season mismatch: expected {season}, but new_df contains {new_season}')
    
    # Column headers check
    existing_col_headings = list(existing_data.columns)
    new_col_headings = list(new_df.columns)
    
    if existing_col_headings != new_col_headings:
        raise ValueError(f"Column headers don't match!\nExisting: {existing_col_headings}\nNew: {new_col_headings}")
    
    print(f"Processing season: {season}")
    
    # Check if the current season exists in the existing data
    if season in existing_data["season"].values:
        print(f"Season {season} found in existing data. Replacing all data for this season...")
        
        # Remove all existing rows for this season
        updated_df = existing_data[existing_data["season"] != season].copy()
        
        # Append all new data for this season
        updated_df = pd.concat([updated_df, new_df], ignore_index=True)
        
        # Sort by season and battleday for cleaner organization
        updated_df = updated_df.sort_values(by=["season", "battleday"]).reset_index(drop=True)
        
        rows_removed = (existing_data["season"] == season).sum()
        rows_added = len(new_df)
        print(f"Removed {rows_removed} existing rows for season {season}")
        print(f"Added {rows_added} new rows for season {season}")
        
    else:
        print(f"Season {season} not found in existing data. Appending as new season...")
        updated_df = pd.concat([existing_data, new_df], ignore_index=True)
        updated_df = updated_df.sort_values(by=["season", "battleday"]).reset_index(drop=True)
        print(f"Added {len(new_df)} rows for new season {season}")
    
    return updated_df

############################################################################################
## Objective of the next part of the code:
# Load each war in the league and filter for those containing the clan tag
# Then save new data to csv file for each war with the relevant clan tag


def Pussay_in_war(battle_tag):
    """Check if the clan is in the war.

    Args:
        battleday_tags (string): battle tag for the war

    Returns:
        bool: True if the clan is in the war, False otherwise
    """
    war_link = f"https://api.clashofclans.com/v1/clanwarleagues/wars/%23{battle_tag[1:]}"
    # war_response = requests.get(f"{base_url}/clans/{clan_tag}/currentwar", headers=headers)
    war_response = requests.get(war_link, headers=headers)

    # Print response code and meaning
    if war_response.status_code != 200:
        print("Error: ", response_codes[war_response.status_code])
        exit()

    war_data = war_response.json() # Keys ['state', 'teamSize', 'preparationStartTime', 'startTime', 'endTime', 'clan', 'opponent', 'warStartTime']
    # "clan" and "opponent" are dictionaries containing the fighting clan's data, these have keys:
    # ['tag', 'name', 'badgeUrls', 'clanLevel', 'attacks', 'stars', 'destructionPercentage', 'members']
    state = war_data["state"]
    if war_data["clan"]["name"] == clan_name or war_data["opponent"]["name"] == clan_name:
        if debug_print_statements:
            print(f"Clan is in war {battle_tag}")   
            print("Clan name: ", war_data["clan"]["name"])
            print("Opponent name: ", war_data["opponent"]["name"])
        return True, state
    
    else:
        if debug_print_statements:
            print(f"Clan is not in war {battle_tag}")  
        return False, state
    
def wars_with_clan(battle_tags):
    """Check which wars in the list contain the clan.

    Args:
        battle_tags (list): list of battle tags to check

    Returns:
        dict: dictionary with the war day as the key and the battle tag as the value, or "#0" if the clan is not in the war
        """
    # 7 day dictionary of war tags containing "#0" for empty tags
    clan_war_tags = {1: "#0", 2: "#0", 3: "#0", 4: "#0", 5: "#0", 6: "#0", 7: "#0"}
    clan_war_states = {1: np.nan, 2: np.nan, 3: np.nan, 4: np.nan, 5: np.nan, 6: np.nan, 7: np.nan}

    # Loop through the rows of the DataFrame
    for row in battle_tags.itertuples():        
        # Find which wartag has Pussay in the war for that day
        for wartag in [row.wartag1, row.wartag2, row.wartag3, row.wartag4]:
            if wartag != "#0": # Skip empty tags
                in_war,war_state = Pussay_in_war(wartag)
                if in_war:
                    print(f"Pussay is in war {wartag} on day {row.battleday} of season {row.season}")
                    clan_war_tags[row.battleday] = wartag
                    clan_war_states[row.battleday] = war_state
                    break # Exit the loop if we found the clan in the war
        # Create error messages
        if clan_war_tags[row.battleday] == "#0":
            print(f"Error: Clan not found in any war on day {row.battleday} of season {row.season}")

    return clan_war_tags, clan_war_states

def Update_Supabase_battle_tags(reduced_warTag_df):
    """Update the Supabase battle_tags table with new battle tags.

    Args:
        reduced_warTag_df (pd.DataFrame): DataFrame containing the battle tags to add to the database
    """
    # Checking for neccessary columns
    required_columns = ["battleday", "wartag", "season"]
    for col in required_columns:
        if col not in reduced_warTag_df.columns:
            raise ValueError(f"Error: Missing required column '{col}' in the DataFrame.")
    
    for row in reduced_warTag_df.itertuples():
        if row.wartag != "#0": # Skip empty tags
            # Check if the battle tag already exists in the database for the same day or season
            existing_tags = supabase.table("battle_tags").select("*").eq("wartag", row.wartag).eq("season", row.season).eq("battleday", row.battleday).execute()
            
            if existing_tags.data:
                print(f"Battle tag {row.wartag} already exists in the database. Skipping insertion.")
            else:
                print(f"Storing battle tag {row.wartag} for day {row.battleday} of season {row.season} to supabase")
                response = store_battle_tag(row.battleday, row.wartag, row.season)
                if response:
                    print(f"Successfully stored battle tag {row.wartag} in the database.")

def save_csv_battle_tags(existing_pussay_data, reduced_warTag_df, season):
    # # Save the reduced battle tag DataFrame to a CSV file
    save_filepath = os.path.join(os.path.dirname(__file__), "Pussay_battle_tags.csv")

    # Check if the file already exists
    if os.path.exists(save_filepath):
        existing_pussay_data = pd.read_csv(save_filepath) # If it exists, load the existing data and append the new data
    else:
        existing_pussay_data = pd.DataFrame(columns=["battleday", "wartag", "season"])# Else, create a new DataFrame with the correct columns

    # # Append the new data to the existing data
    new_pussay_data = append_days_to_dataframe(existing_pussay_data, reduced_warTag_df, season)
    # # Save the new data to the CSV file
    new_pussay_data.to_csv(save_filepath, index=False)
    

def load_battle_tags_supabase(clan_tag, headers= headers):
    """Load existing battle tags from the Supabase battle_tags table.

    Args:
        clan_tag (str): The clan tag of the clan to get the battle tags for.
    """

    if __name__ == "__main__":
        prints = True
    else:
        prints = False
    # Get the battle tags for the current war league
    seasonal_battle_tag_df, season = get_war_tags(clan_tag, headers)
    if prints: print("seasonal battle tag df: ", seasonal_battle_tag_df)

    # Find which wars the clan is in
    clan_war_tags,clan_war_states = wars_with_clan(seasonal_battle_tag_df)    
    if prints: print("Clan war tags for the week:", clan_war_tags)

    # Create a reduced DataFrame with only the war tags containing the clan, columns: battleday, wartag, season
    reduced_warTag_df = pd.DataFrame(columns=["battleday", "wartag", "season"])
    for day, tag in clan_war_tags.items():
        reduced_warTag_df = pd.concat([reduced_warTag_df, pd.DataFrame({"battleday": [day], "wartag": [tag], "season": [season]})], ignore_index=True)
    
    # Save to Supabase battle_tags table
    Update_Supabase_battle_tags(reduced_warTag_df)


if __name__ == "__main__":
    load_battle_tags_supabase(clan_tag, headers)