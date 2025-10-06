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
    "authorization": "Bearer %s" % keys["rory_home"],
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
    
    if len(new_df["season"].unique()) != 1:
        raise ValueError(f'More than 1 season in the new data, new_df.unique = {new_df["season"].unique()}')
    else:
        season = new_df["season"].unique()[0]
    # Check if the current season is already in the DataFrame
    if season in new_df["season"].values:
        print(f"Season {season} is already in the DataFrame.")

        

        # Column headers
        existing_col_headings = existing_data.columns.values
        new_col_headings = existing_data.columns.values
        assert np.array_equal(existing_col_headings, new_col_headings), \
            f"Column headers don't match!\nExisting: {existing_col_headings}\nNew: {new_col_headings}"
        
        # Use bitwise & instead of 'and', and check all varying columns for "#0"
        varying_cols_existing = existing_col_headings[1:-1]  # All columns except battleday and season
        varying_cols_new = new_col_headings[1:-1]

        # Create filter for current season
        season_filt_existing = existing_data["season"] == season
        season_filt_new = new_df["season"] == season

        # Create filter to exclude rows with "#0" in any of the varying columns
        no_zero_filt_existing = ~existing_data[varying_cols_existing].isin(["#0"]).any(axis=1)
        no_zero_filt_new = ~new_df[varying_cols_new].isin(["#0"]).any(axis=1)

        # Combine filters
        filt_existing = season_filt_existing & no_zero_filt_existing
        filt_new = season_filt_new & no_zero_filt_new

        # Find the largest battleday for the current season
        max_battleday_exisiting = existing_data[filt_existing]["battleday"].max()
        max_battleday_new = new_df[filt_new]["battleday"].max()

        print("Max battleday from new data:", max_battleday_new)
        print("Max battleday from exisiting data:", max_battleday_exisiting)

        if max_battleday_new != max_battleday_exisiting:
            updated_df = existing_data.copy()

            update_filt = (updated_df["battleday"] > max_battleday_exisiting) & (updated_df["season"]==season)
            new_filt = (updated_df["battleday"] > max_battleday_exisiting) & (updated_df["season"]==season)
            
            # Get the varying columns (everything except battleday and season)
            varying_cols = new_col_headings[1:-1]
            
            # Replace the varying columns with new data
            updated_df.loc[update_filt, varying_cols] = new_df.loc[new_filt, varying_cols].values
            
            print(f"Updated {update_filt.sum()} rows for battledays > {max_battleday_exisiting}")
            
        else:
            print("No new battledays to update")
            updated_df = existing_data.copy()
            
        # # Append data for the current season over the max battleday
        # append_data = new_df[(new_df["season"] == season) & (new_df["battleday"] > max_battleday_exisiting)]
        # newdata = pd.concat([existing_data, append_data], ignore_index=True)
    else:
        print(f"Season {season} is not in the DataFrame.")
        updated_df = pd.concat([existing_data, new_df], ignore_index=True)
    
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
    
def wars_with_clan(battle_tags):
    """Check which wars in the list contain the clan.

    Args:
        battle_tags (list): list of battle tags to check

    Returns:
        dict: dictionary with the war day as the key and the battle tag as the value, or "#0" if the clan is not in the war
        """
    # 7 day dictionary of war tags containing "#0" for empty tags
    clan_war_tags = {1: "#0", 2: "#0", 3: "#0", 4: "#0", 5: "#0", 6: "#0", 7: "#0"}

    # Loop through the rows of the DataFrame
    for row in battle_tags.itertuples():        
        # Find which wartag has Pussay in the war for that day
        for wartag in [row.wartag1, row.wartag2, row.wartag3, row.wartag4]:
            if wartag != "#0": # Skip empty tags
                in_war = Pussay_in_war(wartag)
                if in_war:
                    print(f"Pussay is in war {wartag} on day {row.battleday} of season {row.season}")
                    clan_war_tags[row.battleday] = wartag
                    break # Exit the loop if we found the clan in the war
        # Create error messages
        if clan_war_tags[row.battleday] == "#0":
            print(f"Error: Clan not found in any war on day {row.battleday} of season {row.season}")

    return clan_war_tags

if __name__ == "__main__":
    # Get the battle tags for the current war league
    seasonal_battle_tag_df, season = get_war_tags(clan_tag, headers)
    print("seasonal battle tag df: ", seasonal_battle_tag_df)

    # Save the battle tag DataFrame to a CSV file
    save_filepath = os.path.join(os.path.dirname(__file__), "battle_tags.csv")
    existing_data = pd.read_csv(save_filepath)
    newdata = append_days_to_dataframe(existing_data, seasonal_battle_tag_df, season)
    # newdata.to_csv(save_filepath, index=False)

    # Print the DataFrame
    print("Battle tag DataFrame:")
    print(newdata.tail(8))

    # Find which wars the clan is in
    clan_war_tags = wars_with_clan(seasonal_battle_tag_df)    
    print("Clan war tags for the week:", clan_war_tags)
    # Create a reduced DataFrame with only the war tags containing the clan, columns: battleday, wartag, season
    reduced_warTag_df = pd.DataFrame(columns=["battleday", "wartag", "season"])
    for day, tag in clan_war_tags.items():
        reduced_warTag_df = pd.concat([reduced_warTag_df, pd.DataFrame({"battleday": [day], "wartag": [tag], "season": [season]})], ignore_index=True)
    # print("Reduced war tag DataFrame:")
    # print(reduced_warTag_df)

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
    # new_pussay_data.to_csv(save_filepath, index=False)

    print("Reduced battle tag DataFrame:")
    print(new_pussay_data)