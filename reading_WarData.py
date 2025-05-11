import pandas as pd
import numpy as np
import requests
import os

# Dictionary containing the API key, add your own key for your IP address
# You can get your own key from https://developer.clashofclans.com
keys = {"rory": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImZmNThkODRjLTVmYWItNDc3Ny1iY2M0LTA5OTc3ZGRjYWM4ZSIsImlhdCI6MTczODU4NzUyOSwic3ViIjoiZGV2ZWxvcGVyLzM3MjExZmI5LTgzODMtNDA1OS05MDFlLTFlNmFmZDBmYzFkNCIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjgyLjQ3LjMzLjE2MyJdLCJ0eXBlIjoiY2xpZW50In1dfQ.QOKe0Vjh2nVam7H8KM3feYh0c8sPQcR_gLRDhUWjCBYjKUgFBxTrgOaWb3BvzKx-X3Ae0OrrcEk6II7y_JmZGw"}

# Pussay Clan Tag
clan_tag = "%23CQGY2LQU"
clan_name = "Pussay Palace"
base_url = "https://api.clashofclans.com/v1"
url = base_url + f"/clans/{clan_tag}"
headers = {
    "Accept": "application/json",
    "authorization": "Bearer %s" % keys["rory"],
}
debug_print_statements = False

Pussay_wars_df = pd.read_csv(os.path.join(os.path.dirname(__file__), "Pussay_battle_tags.csv"))
if debug_print_statements:
    print("Pussay war tags: \n", Pussay_wars_df)

Pussay_warTags = Pussay_wars_df["wartag"]

# Load a war
battle_tag = Pussay_warTags[0]
def get_war_stats(battle_tag):
    """This function retrieves the war stats for a given battle tag from the Clash of Clans API for the 'Pussay Palace' clan.

    Args:
        battle_tag (string): The battle tag of the war to retrieve stats for.

    Returns:
        Pussay_members_df (pd.DataFrame): A DataFrame containing the war stats for each member of the 'Pussay Palace' clan.
    """
    war_link = f"https://api.clashofclans.com/v1/clanwarleagues/wars/{battle_tag.replace("#", "%23")}"
    if debug_print_statements: print("Pussay war link: ", war_link)

    # Make the request to the API
    war_response = requests.get(war_link, headers=headers)
    war_data = war_response.json()
    if debug_print_statements: 
        print("War response code: ", war_response, "\nPussay war data keys: ", war_data.keys())
        print(war_data["clan"]["members"][2].keys()) # keys: ['tag', 'name', 'townhallLevel', 'mapPosition', 'attacks', 'opponentAttacks', 'bestOpponentAttack']

    #### Want a dataframe for each member countaining the following:
    # Name, Battleday, TH level, Attack stars, Attack %, Attack Duration, Defense stars, Defense %, Opponent TH level, season

    # Finding if Pussay is stored as clan or opponent
    Pussay_clan_or_opponent = "clan" if war_data["clan"]["name"] == clan_name else "opponent"
    Opponent_clan_or_opponent = "opponent" if Pussay_clan_or_opponent == "clan" else "clan"
    if debug_print_statements:
        print("Pussay clan or opponent: ", Pussay_clan_or_opponent)
        print("Opponent clan name: ", war_data[Opponent_clan_or_opponent]["name"])

    ### Accessing the attack and defense information for a member
    Pussay_members_df = pd.DataFrame(columns=["name", "townHallLevel", "attackStars", "attackPercentage", "attackDuration", "defenseStars", "defensePercentage", "defenseDuration", "opponentTHLevel"])
    for member_index in range(len(war_data[Pussay_clan_or_opponent]["members"])):
        member_info = war_data[Pussay_clan_or_opponent]["members"][member_index]
        
        # if debug_print_statements:
            # print(war_data["clan"]["members"][member_index].keys())  # Access: attack stars,%, Attack duration
            # print(war_data["clan"]["members"][member_index]["bestOpponentAttack"]) # Access: Defense stars,%, Defense duration
            # print("Member info: ", member_info)
            # print("Member keys: ", member_info.keys()) # keys: ['tag', 'name', 'townhallLevel', 'mapPosition', 'attacks', 'opponentAttacks', 'bestOpponentAttack']

        member_th_level = member_info["townhallLevel"]
        if "attacks" not in member_info or member_info["attacks"] is None:
            attack_stars = np.nan
            attack_percentage = np.nan
            attack_duration = np.nan
            if debug_print_statements: print(f"Member '{member_info['name']}' has not attacked.")
            

        else:
            attack_stars = member_info["attacks"][0]["stars"]
            attack_percentage = member_info["attacks"][0]["destructionPercentage"]
            attack_duration = member_info["attacks"][0]["duration"]
            

        # Filtering if the member has been attacked
        if member_info["opponentAttacks"] > 0:
            defense_stars = member_info["bestOpponentAttack"]["stars"]
            defense_percentage = member_info["bestOpponentAttack"]["destructionPercentage"]
            defense_duration = member_info["bestOpponentAttack"]["duration"]

            # Finding the opponent's TH level
            Opponent_tags = member_info["bestOpponentAttack"]["attackerTag"]
            for member in war_data[Opponent_clan_or_opponent]["members"]:
                if member["tag"] == Opponent_tags:
                    opponent_th_level = member["townhallLevel"]
                    break
            if debug_print_statements: print("Opponent TH level:", opponent_th_level, " Member TH level: ", member_th_level)
            
        else:
            defense_stars = np.nan
            defense_percentage = np.nan
            defense_duration = np.nan
            opponent_th_level = np.nan
            if debug_print_statements:  print("No opponent attacks")

        member_battleday_stats = {
            "name": member_info["name"], 
            "townHallLevel": member_th_level,
            "attackStars": attack_stars,
            "attackPercentage": attack_percentage,
            "attackDuration": attack_duration,
            "defenseStars": defense_stars,
            "defensePercentage": defense_percentage,
            "defenseDuration": defense_duration,
            "opponentTHLevel": opponent_th_level,
            # "season": war_data["season"]["id"],
        }
        # Adding the member's stats to the dataframe
        Pussay_members_df.loc[len(Pussay_members_df)] = member_battleday_stats
    return Pussay_members_df

# Creating a dataframe to store the battle day stats
base_df = pd.DataFrame(columns=["name", "townHallLevel", "attackStars", "attackPercentage", "attackDuration", "defenseStars", "defensePercentage", "defenseDuration", "opponentTHLevel", "battleday", "season"])

# Loop through all the battle tags and get the stats for each day
for i,battle_tag in enumerate(Pussay_wars_df["wartag"]):
    battle_day = i + 1
    season = Pussay_wars_df["season"][i]
    
    battle_day_df = get_war_stats(battle_tag)
    battle_day_df["battleday"] = battle_day
    battle_day_df["season"] = season
    
    # Add the battle day and season to the dataframe
    for _, row in battle_day_df.iterrows():
        base_df.loc[len(base_df)] = row