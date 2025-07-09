import pandas as pd
import numpy as np
import requests
import os
import json

# Dictionary containing the API key, add your own key for your IP address
# You can get your own key from https://developer.clashofclans.com
# Load API keys from a JSON file

keys_file_path = os.path.join(os.path.dirname(__file__), "keys.json")
with open(keys_file_path, "r") as keys_file:
    keys = json.load(keys_file)

# Pussay Clan Tag
clan_tag = "%23CQGY2LQU"
clan_name = "Pussay Palace"
base_url = "https://api.clashofclans.com/v1"
url = base_url + f"/clans/{clan_tag}"
headers = {
    "Accept": "application/json",
    "authorization": "Bearer %s" % keys["rory_desktop"],
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


# Accessing CWL information
leaguegroup_url = f"{base_url}/clans/{clan_tag}/currentwar/leaguegroup"
leaguegroup_response = requests.get(leaguegroup_url, headers=headers)
print("League group response status code:", leaguegroup_response.status_code)
leaguegroup_data = leaguegroup_response.json()  # Keys: ['state', 'season', 'clans', 'rounds'])
# print("League group keys: ", leaguegroup_data.keys())
season = leaguegroup_data["season"]
# print("League Other Clan members: ", leaguegroup_data["clans"][0].keys()) # Index for other clans in league group
# print(leaguegroup_data)

# Create a DataFrame to store battle tags in
battle_tag_df = pd.DataFrame(columns=["battleday", "wartag1", "wartag2", "wartag3", "wartag4", "season"])

# Tags each war in the league group
cwl_war_tags = leaguegroup_data["rounds"]
for i,battleday_tags in enumerate(cwl_war_tags):
    battleday_tags = battleday_tags["warTags"]
    battle_tag_df.loc[i] = [i+1, battleday_tags[0], battleday_tags[1], battleday_tags[2], battleday_tags[3], season]

def append_days_to_dataframe(existing_data, new_df, season):
    """Append new battleday data to the existing DataFrame for the current season.

    Args:
        existing_data (pd.DataFrame): existing DataFrame containing battle tags from previous seasons and the current season (if any)
        new_df (pd.DataFrame): DataFrame containing new battle tags for the current season
        season (str): string of the season to append data for

    Returns:
        pd.DataFrame: DataFrame with the new battleday data appended
    """
    # Check if the current season is already in the DataFrame
    if season in existing_data["season"].values:
        print(f"Season {season} is already in the DataFrame.")
        # Filter the existing data for the current season
        filt = existing_data["season"] == season

        # Find the largest battleday for the current season
        max_battleday = existing_data[filt]["battleday"].max()
        print("Max battleday for current season:", max_battleday)

        # Append data for the current season over the max battleday
        append_data = new_df[(new_df["season"] == season) & (new_df["battleday"] > max_battleday)]
        newdata = pd.concat([existing_data, append_data], ignore_index=True)
    else:
        print(f"Season {season} is not in the DataFrame.")
        newdata = pd.concat([existing_data, new_df], ignore_index=True)
    
    return newdata

# Save the battle tag DataFrame to a CSV file
save_filepath = os.path.join(os.path.dirname(__file__), "battle_tags.csv")
existing_data = pd.read_csv(save_filepath)
newdata = append_days_to_dataframe(existing_data,battle_tag_df, season)
newdata.to_csv(save_filepath, index=False)

# Print the DataFrame
print("Battle tag DataFrame:")
print(newdata)

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

    war_data = war_response.json() # Keys ['state', 'teamSize', 'preparationStartTime', 'startTime', 'endTime', 'clan', 'opponent', 'warStartTime']
    # "clan" and "opponent" are dictionaries containing the fighting clan's data, these have keys:
    # ['tag', 'name', 'badgeUrls', 'clanLevel', 'attacks', 'stars', 'destructionPercentage', 'members']
    
    if war_data["clan"]["name"] == clan_name or war_data["opponent"]["name"] == clan_name:
        if debug_print_statements:
            print(f"Clan is in war {battle_tag}")   
            print("Clan name: ", war_data["clan"]["name"])
            print("Opponent name: ", war_data["opponent"]["name"])
        return True
    
    else:
        if debug_print_statements:
            print(f"Clan is not in war {battle_tag}")  
        return False
    
# Find which wars the clan is in
reduced_warTag_df = pd.DataFrame(columns=["battleday", "wartag", "season"])
# Loop through the days
for day, battle_day_tags in enumerate(cwl_war_tags):
    battleday_tags = battle_day_tags["warTags"]

    # Loop through the battle tags for each day
    for battle_tag in battleday_tags:
        # Check if the clan is in the war
        in_war = Pussay_in_war(battle_tag)
        # If the clan is in the war, add the battle tag to the DataFrame
        if in_war:
            reduced_warTag_df.loc[len(reduced_warTag_df)] = [day+1, battle_tag, season]
            if debug_print_statements:
                print("Added to reduced DataFrame: ", battle_tag)

# Save the reduced battle tag DataFrame to a CSV file
save_filepath = os.path.join(os.path.dirname(__file__), "Pussay_battle_tags.csv")

# Check if the file already exists
if os.path.exists(save_filepath):
    existing_pussay_data = pd.read_csv(save_filepath) # If it exists, load the existing data and append the new data
else:
    existing_pussay_data = pd.DataFrame(columns=["battleday", "wartag", "season"])# Else, create a new DataFrame

# Append the new data to the existing data
new_pussay_data = append_days_to_dataframe(existing_pussay_data, reduced_warTag_df, season)
# Save the new data to the CSV file
new_pussay_data.to_csv(save_filepath, index=False)

print("Reduced battle tag DataFrame:")
print(new_pussay_data)