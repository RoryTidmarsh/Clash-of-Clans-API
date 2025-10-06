import pandas as pd
import numpy as np
import requests
import os
import json
from datetime import datetime
import sys
import io

# Force UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Dictionary containing the API key, add your own key for your IP address
# You can get your own key from https://developer.clashofclans.com
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
    "authorization": "Bearer %s" % keys["rory_home"]
}
debug_print_statements = False

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

class member():
    def __init__(self, member_json):
        self.tag = member_json["tag"]
        self.name = member_json["name"]
        self.townhallLevel = member_json["townhallLevel"]
        self.mapPosistion = member_json["mapPosition"]

        self.attacker_townhallLevel = np.nan    #TH level of the opponent that is attacking us
        self.defender_townhallLevel = np.nan    #TH level of the opponent we attacked
        self.attack_th_diff = np.nan    # TH diff compared to the opponent we attacked
        self.defense_th_diff = np.nan   # TH diff compared to the opponent that attacked us
        
        if "attacks" not in member_json or member_json["attacks"] is None:
            self.attack_stars = np.nan
            self.attack_percentage = np.nan
            self.attack_duration = np.nan
            self.defender_tag = np.nan  # Tag of person we attack
            if debug_print_statements: print(f"Member '{member_json['name']}' has not attacked.")

        else:
            self.attack_stars = member_json["attacks"][0]["stars"]
            self.attack_percentage = member_json["attacks"][0]["destructionPercentage"]
            self.attack_duration = member_json["attacks"][0]["duration"]
            self.defender_tag = member_json["attacks"][0]["defenderTag"]    # Tag of person we attack

        if "bestOpponentAttack" not in member_json or member_json["bestOpponentAttack"] is None:
            self.defense_stars = np.nan
            self.defense_percentage = np.nan
            self.defense_duration = np.nan
            self.attacker_tag = np.nan  # Opponent that attacks our clan
            if debug_print_statements: print(f"Member '{member_json['name']}' has not been attacked.")

        else:
            self.defense_stars = member_json["bestOpponentAttack"]["stars"]
            self.defense_percentage = member_json["bestOpponentAttack"]["destructionPercentage"]
            self.defense_duration = member_json["bestOpponentAttack"]["duration"]
            self.attacker_tag = member_json["bestOpponentAttack"]["attackerTag"]     # Opponent that attacks our clan

    def __repr__(self):
        if not np.isnan(self.attack_stars):
            th_diff = self.attack_th_diff if not np.isnan(self.defender_townhallLevel) else "?"
            th_info = f" (TH{th_diff:+d})" if th_diff != "?" else ""
            attack_info = f"{self.attack_stars}★ ({self.attack_percentage}%) vs {self.defender_tag}{th_info}"
        else:
            attack_info = "No attack"
        
        if not np.isnan(self.defense_stars):
            th_diff = self.defense_th_diff if not np.isnan(self.attacker_townhallLevel) else "?"
            th_info = f" (TH{th_diff:+d})" if th_diff != "?" else ""
            defense_info = f"{self.defense_stars}★ ({self.defense_percentage}%) from {self.attacker_tag}{th_info}"
        else:
            defense_info = "Not attacked"
        
        return (f"Member({self.name}, tag={self.tag}, TH{self.townhallLevel}, pos={self.mapPosistion})\n"
                f"  Attack: {attack_info}\n"
                f"  Defense: {defense_info}")

    def find_attacker_TH_level(self, opponent_member_json):
        # self.attacker_tag
        # Opponent_tags = opponent_member_json["attackerTag"]

        # Find the TH level of the person we attacked
        if self.defender_tag != np.nan:
            for opponent in opponent_member_json["members"]:
                if opponent["tag"] == self.defender_tag:
                    self.defender_townhallLevel = opponent["townhallLevel"]
                    break

        # Find the TH level of the person that attacked us
        if self.attacker_tag != np.nan:
            for opponent in opponent_member_json["members"]:
                if opponent["tag"] == self.attacker_tag:
                    self.attacker_townhallLevel = opponent["townhallLevel"]
                    break

        self.attack_th_diff = (self.defender_townhallLevel - self.townhallLevel 
                        if not np.isnan(self.defender_townhallLevel) else np.nan)
        self.defense_th_diff = (self.attacker_townhallLevel - self.townhallLevel 
                        if not np.isnan(self.attacker_townhallLevel) else np.nan)

        if debug_print_statements: print(f"attacker TH level {self.attacker_townhallLevel}, defender TH level {self.defender_townhallLevel}")

    def to_dataframe_row(self):
        """Returns a dictionary of all member attributes suitable for adding to a DataFrame."""
        # Calculate TH differences
        # attack_th_diff = (self.defender_townhallLevel - self.townhallLevel 
        #                 if not np.isnan(self.defender_townhallLevel) else np.nan)
        # defense_th_diff = (self.attacker_townhallLevel - self.townhallLevel 
        #                 if not np.isnan(self.attacker_townhallLevel) else np.nan)
        
        return {
            'tag': self.tag,
            'name': self.name,
            'townhallLevel': self.townhallLevel,
            'mapPosition': self.mapPosistion,
            'attacker_townhallLevel': self.attacker_townhallLevel,
            'defender_townhallLevel': self.defender_townhallLevel,
            'attack_th_diff': self.attack_th_diff,  # Positive means attacked higher TH
            'defense_th_diff': self.defense_th_diff,  # Positive means defended against higher TH
            'attack_stars': self.attack_stars,
            'attack_percentage': self.attack_percentage,
            'attack_duration': self.attack_duration,
            'defender_tag': self.defender_tag,
            'defense_stars': self.defense_stars,
            'defense_percentage': self.defense_percentage,
            'defense_duration': self.defense_duration,
            'attacker_tag': self.attacker_tag
        }
               
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

    if war_response.status_code != 200:
        error_msg = response_codes.get(war_response.status_code, "Unknown error")
        raise ValueError(f"API request failed with status code {war_response.status_code}: {error_msg}")

    print(battle_tag, war_response)
    war_data = war_response.json()

    # Check if clan is in a war or if war data is accessible
    if "state" in war_data:
        state = war_data["state"]
        if state == "notInWar":
            raise ValueError(f'Clan is not in war. Current state: "{state}"')
        elif state in ["inWar", "warEnded", "preparation"]:
            print(f'War state: "{state}"')
        else:
            print(f"Warning: Unexpected war state: {state}")
    elif "clan" not in war_data:
        raise ValueError(f"Clan War not accessible. War occurred too long ago or data is unavailable. War state: {war_data["state"]}")
    
    #### Want a dataframe for each member countaining the following:
    # Name, Battleday, TH level, Attack stars, Attack %, Attack Duration, Defense stars, Defense %, Opponent TH level, season

    
    # # Finding if Pussay is stored as clan or opponent
    Pussay_clan_or_opponent = "clan" if war_data["clan"]["name"] == clan_name else "opponent"
    Opponent_clan_or_opponent = "opponent" if Pussay_clan_or_opponent == "clan" else "clan"
    if debug_print_statements:
        print("Pussay clan or opponent: ", Pussay_clan_or_opponent)
        print("Opponent clan name: ", war_data[Opponent_clan_or_opponent]["name"])

    # Empty array to store data in
    member_array = []

    # Search through each member and collect data
    for member_index in range(len(war_data[Pussay_clan_or_opponent]["members"])):
        member_info = war_data[Pussay_clan_or_opponent]["members"][member_index]
        
        # Collect data using 'member' class
        clan_member = member(member_info)
        clan_member.find_attacker_TH_level(war_data[Opponent_clan_or_opponent])

        member_array.append(clan_member)
        print(clan_member)
    assert len(member_array) == len(war_data[Pussay_clan_or_opponent]["members"])

    # Store information in a dataframe
    war_info_df = pd.DataFrame([m.to_dataframe_row() for m in member_array])

    return war_info_df, war_data["state"]

class WarDataManager:
    def __init__(self, status_file_path="war_status.csv", data_folder="war_data"):
        """
        Initialize the War Data Manager
        
        Args:
            status_file_path: Path to CSV tracking war status
            data_folder: Folder where individual war data files are stored
        """
        self.status_file_path = status_file_path
        self.data_folder = data_folder
        
        # Create data folder if it doesn't exist
        os.makedirs(data_folder, exist_ok=True)
        
        # Load or create status tracking file
        if os.path.exists(status_file_path):
            self.status_df = pd.read_csv(status_file_path)
        else:
            self.status_df = pd.DataFrame(columns=[
                'wartag', 'COC_war_status', 'loading_status', 'last_updated', 'data_file'
            ])

    def should_load_war(self, wartag):
        """
        Check if a war should be loaded from the API
        
        Args:
            wartag: The war tag to check
            
        Returns:
            bool: True if war should be loaded, False if it can be skipped
        """
        # Check if war tag exists in status tracking
        war_status = self.status_df[self.status_df['wartag'] == wartag]
        
        if war_status.empty:
            # War not tracked yet, should load
            print(f"War {wartag} not tracked yet. Will load.")
            return True
        
        loading_status = war_status.iloc[0]['loading_status']
        coc_status = war_status.iloc[0]['COC_war_status']
        
        # skip if loading_status is 'completed'
        if loading_status == 'completed':
            print(f"War {wartag} already completed (COC status: {coc_status}). Skipping.")
            return False
        
        # Reload if 'notLoaded' or 'inProgress'
        print(f"War {wartag} loading status: {loading_status}, COC status: {coc_status}. Will reload.")
        return True
    
    def determine_loading_status(self, coc_war_status):
        """
        Determine the loading_status based on COC war status
        
        Args:
            coc_war_status: Status returned from COC API
            
        Returns:
            str: loading_status ('notLoaded', 'inProgress', or 'completed')
        """
        if coc_war_status == "warEnded":
            return "completed"
        elif coc_war_status in ["inWar", "preparation"]:
            return "inProgress"
        else:
            # This shouldn't normally happen, but default to notLoaded
            return "notLoaded"
        
    def get_war_data_path(self, wartag):
        """Generate file path for storing war data"""
        # Clean the wartag for use in filename
        clean_tag = wartag.replace('#', '').replace('%23', '')
        return os.path.join(self.data_folder, f"war_{clean_tag}.csv")
    
    def save_war_data(self, wartag, war_df, coc_war_status):
        """
        Save war data and update status tracking
        
        Args:
            wartag: The war tag
            war_df: DataFrame containing war data
            coc_war_status: Current status of the war from COC API 
                           ('inWar', 'warEnded', 'preparation')
        """
        # Save the war data
        data_path = self.get_war_data_path(wartag)
        war_df.to_csv(data_path, index=False)
        
        # Determine loading status based on COC war status
        loading_status = self.determine_loading_status(coc_war_status)
        
        # Update status tracking
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Remove existing entry if present
        self.status_df = self.status_df[self.status_df['wartag'] != wartag]
        
        # Add new entry
        new_row = pd.DataFrame([{
            'wartag': wartag,
            'COC_war_status': coc_war_status,
            'loading_status': loading_status,
            'last_updated': current_time,
            'data_file': data_path
        }])
        
        self.status_df = pd.concat([self.status_df, new_row], ignore_index=True)
        
        # Save status file
        self.status_df.to_csv(self.status_file_path, index=False)
        
        status_symbol = "✓" if loading_status == "completed" else "⋯"
        print(f"{status_symbol} Saved war {wartag} | COC: {coc_war_status} | Loading: {loading_status}")

    def load_cached_war_data(self, wartag):
        """
        Load previously saved war data if available
        
        Args:
            wartag: The war tag
            
        Returns:
            pd.DataFrame or None: War data if available, None otherwise
        """
        data_path = self.get_war_data_path(wartag)
        
        if os.path.exists(data_path):
            return pd.read_csv(data_path)
        return None
    
    def process_war(self, wartag, get_war_stats_func, season=None, cwl_day=None):
        """
        Process a single war - either load from cache or fetch from API
        
        Args:
            wartag: The war tag
            get_war_stats_func: Function to call to get war stats from API
                               Should return (war_df, coc_war_status)
            season: Season identifier (e.g., "2025-10") - will be added to DataFrame
            cwl_day: CWL day number (e.g., 1-7) - will be added to DataFrame
            
        Returns:
            tuple: (war_df, coc_war_status, loading_status, was_cached)
        """
        # Check if we should load from API
        if not self.should_load_war(wartag):
            # Load from cache
            cached_data = self.load_cached_war_data(wartag)
            if cached_data is not None:
                war_status = self.status_df[self.status_df['wartag'] == wartag].iloc[0]
                # Add season and cwl_day if not already present
                if season is not None and 'season' not in cached_data.columns:
                    cached_data['season'] = season
                if cwl_day is not None and 'cwl_day' not in cached_data.columns:
                    cached_data['cwl_day'] = cwl_day
                return (
                    cached_data, 
                    war_status['COC_war_status'],
                    war_status['loading_status'],
                    True
                )
        
        # Load from API
        try:
            war_df, coc_war_status = get_war_stats_func(wartag)
            
            # Add season and cwl_day columns
            if season is not None:
                war_df['season'] = season
            if cwl_day is not None:
                war_df['cwl_day'] = cwl_day
            
            # Determine loading status
            loading_status = self.determine_loading_status(coc_war_status)
            
            # Save the data
            self.save_war_data(wartag, war_df, coc_war_status)
            
            return war_df, coc_war_status, loading_status, False
            
        except Exception as e:
            print(f"Error loading war {wartag}: {e}")
            # Try to return cached data if available
            cached_data = self.load_cached_war_data(wartag)
            if cached_data is not None:
                print(f"⚠ Returning cached data for {wartag} due to API error")
                war_status = self.status_df[self.status_df['wartag'] == wartag].iloc[0]
                # Add season and cwl_day if not already present
                if season is not None and 'season' not in cached_data.columns:
                    cached_data['season'] = season
                if cwl_day is not None and 'cwl_day' not in cached_data.columns:
                    cached_data['cwl_day'] = cwl_day
                return (
                    cached_data,
                    war_status['COC_war_status'],
                    war_status['loading_status'],
                    True
                )
            raise
    
    def get_status_summary(self):
        """
        Get a summary of all tracked wars
        
        Returns:
            dict: Summary statistics
        """
        if self.status_df.empty:
            return {
                'total_wars': 0,
                'completed': 0,
                'in_progress': 0,
                'not_loaded': 0
            }
        
        return {
            'total_wars': len(self.status_df),
            'completed': len(self.status_df[self.status_df['loading_status'] == 'completed']),
            'in_progress': len(self.status_df[self.status_df['loading_status'] == 'inProgress']),
            'not_loaded': len(self.status_df[self.status_df['loading_status'] == 'notLoaded'])
        }
    
    def __repo__(self):
        """Print a formatted summary of war statuses"""
        summary = self.get_status_summary()
        print("\n" + "="*50)
        print("WAR DATA STATUS SUMMARY")
        print("="*50)
        print(f"Total Wars Tracked:     {summary['total_wars']}")
        print(f"✓ Completed:            {summary['completed']}")
        print(f"⋯ In Progress:          {summary['in_progress']}")
        print(f"○ Not Loaded:           {summary['not_loaded']}")
        print("="*50 + "\n")
    

def gather_season_data(season):
    """This function retrieves the war stats for a given season from the Clash of Clans API for the 'Pussay Palace' clan.

    Args:
        season (string): The season to retrieve stats for.

    Returns:
        base_df (pd.DataFrame): A DataFrame containing the war stats for each member for each battle day of the 'Pussay Palace' clan for the given season.
    """
    # Creating a dataframe to store the battle day stats
    base_df = pd.DataFrame(columns=["name", "townHallLevel", "attackStars", "attackPercentage", "attackDuration", "defenseStars", "defensePercentage", "defenseDuration", "opponentTHLevel", "battleday", "season"])

    season_wars_df = Pussay_wars_df[Pussay_wars_df["season"] == season]
    
    # Loop through all the battle tags and get the stats for each day
    for i in range(len(season_wars_df)):
        battle_tag = season_wars_df["wartag"][i]
        battle_day = season_wars_df["battleday"][i]
        
        battle_day_df = get_war_stats(battle_tag)
        battle_day_df["battleday"] = battle_day
        battle_day_df["season"] = season
        
        # Add the battle day and season to the dataframe
        for _, row in battle_day_df.iterrows():
            base_df.loc[len(base_df)] = row

    return base_df


if __name__ == "__main__":
    Pussay_wars_df = pd.read_csv(os.path.join(os.path.dirname(__file__), "Pussay_battle_tags.csv"))
    if debug_print_statements:
        print("Pussay war tags: \n", Pussay_wars_df)

    Pussay_warTags = Pussay_wars_df["wartag"]
    print(Pussay_warTags)
    #Finding the most recent war

    # Load war data
    war_info_df, war_state  = get_war_stats(Pussay_warTags[17]) #"#8Q9208GJ0"

    print(war_info_df.info())




# # Load the season data
# season_data = gather_season_data("2025-10")
# print(season_data.info())

# # Path to the combined database CSV
# db_filepath = os.path.join(os.path.dirname(__file__), "Seasons Data", "Pussay_season_database.csv")

# # Load existing database if it exists
# if os.path.exists(db_filepath):
#     all_seasons_df = pd.read_csv(db_filepath)
# else:
#     all_seasons_df = pd.DataFrame(columns=season_data.columns)

# # Check if this season is already present and complete
# season_rows = all_seasons_df[all_seasons_df["season"] == season_data["season"][0]]
# if len(season_rows) < 15 * 7:
#     # Remove any partial/incomplete data for this season
#     all_seasons_df = all_seasons_df[all_seasons_df["season"] != season_data["season"][0]]
#     # Append the new season data
#     all_seasons_df = pd.concat([all_seasons_df, season_data], ignore_index=True)
#     # Save the updated database
#     all_seasons_df.to_csv(db_filepath, index=False)
#     print(f"Added/updated season {season_data['season'][0]} to database.")
# else:
#     print(f"Season {season_data['season'][0]} already complete in database.")
# # Save the season data to a CSV file
# save_filepath = os.path.join(os.path.dirname(__file__), f"Seasons Data\\Pussay_season_data_{season_data['season'][0]}.csv")
# season_data.to_csv(save_filepath, index=False)