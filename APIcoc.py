import pandas as pd
import numpy as np
import requests
import os

# Dictionary containing the API key, add your own key for your IP address
# You can get your own key from https://developer.clashofclans.com
keys = {"rory": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImZmNThkODRjLTVmYWItNDc3Ny1iY2M0LTA5OTc3ZGRjYWM4ZSIsImlhdCI6MTczODU4NzUyOSwic3ViIjoiZGV2ZWxvcGVyLzM3MjExZmI5LTgzODMtNDA1OS05MDFlLTFlNmFmZDBmYzFkNCIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjgyLjQ3LjMzLjE2MyJdLCJ0eXBlIjoiY2xpZW50In1dfQ.QOKe0Vjh2nVam7H8KM3feYh0c8sPQcR_gLRDhUWjCBYjKUgFBxTrgOaWb3BvzKx-X3Ae0OrrcEk6II7y_JmZGw"}

# Pussay Clan Tag
clan_tag = "%23CQGY2LQU"
base_url = "https://api.clashofclans.com/v1"
url = base_url + f"/clans/{clan_tag}"
headers = {
    "Accept": "application/json",
    "authorization": "Bearer %s" % keys["rory"],
}

# Make the request to the API
response = requests.request("GET", url, headers=headers)
data = response.json()
print(data.keys())
# Find rozzledog72 in the member list and print their tag and role
for member in data["memberList"]:
    if member["name"] == "rozzledog 72":
        print("Name:", member["name"])
        print("Role:", member["role"])
        print("Trophies:", member["trophies"])
        print("TH level:",member["townHallLevel"])


# Accessing clan war log
response_warlog = requests.request("GET", url + "/warlog", headers=headers)
data_warlog = response_warlog.json()
print("War log keys: ", data_warlog["items"][0].keys()) # Keys: ['result', 'endTime', 'teamSize', 'attacksPerMember', 'battleModifier', 'clan', 'opponent']


# Accessing CWL information
leaguegroup_url = f"{base_url}/clans/{clan_tag}/currentwar/leaguegroup"
leaguegroup_response = requests.get(leaguegroup_url, headers=headers)
leaguegroup_data = leaguegroup_response.json()  # Keys: ['state', 'season', 'clans', 'rounds'])
print("League group keys: ", leaguegroup_data.keys())
season = leaguegroup_data["season"]
print("League Other Clan members: ", leaguegroup_data["clans"][0].keys()) # Index for other clans in league group

# Create a DataFrame to store battle tags in
battle_tag_df = pd.DataFrame(columns=["battleday", "wartag1", "wartag2", "wartag3", "wartag4", "season"])

# Tags each war in the league group
cwl_war_tags = leaguegroup_data["rounds"]
for i,battleday_tags in enumerate(cwl_war_tags):
    battleday_tags = battleday_tags["warTags"]
    # print(f"Battleday {i+1} tags:", battleday_tags)

    battle_tag_df.loc[i] = [i+1, battleday_tags[0], battleday_tags[1], battleday_tags[2], battleday_tags[3], season]
    # for j, war_tag in enumerate(battleday_tags):

    #     war_url = f"{base_url}/clans/{clan_tag}/currentwar/leaguegroup/{war_tag}"
    #     war_response = requests.get(war_url, headers=headers)   # Get the war data for each war tag, can take a while to load
    #     war_data = war_response.json()
    #     print(f"War {j+1} keys: ", war_data.keys())

# Print the battle tag DataFrame
print(battle_tag_df)

# Save the battle tag DataFrame to a CSV file
save_filepath = os.path.join(os.path.dirname(__file__), "battle_tags.csv")
battle_tag_df.to_csv(save_filepath, index=False)