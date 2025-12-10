import pandas as pd
import numpy as np
import requests
import sys
import io
import os
from datetime import datetime
from refresh.supabaseRefresh import supabase
from refresh.COC_client import clan_data, response_codes

# Force UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Pussay Clan Tag
clan_tag = clan_data["clan_tag"]
clan_name = clan_data["clan_name"]
base_url = clan_data["base_url"]
url = clan_data["url"]
headers = clan_data["headers"]

debug_print_statements = False

WAR_DATA_SCHEMA = {
    'tag': str,
    'name': str,
    'townhallLevel': int,
    'mapPosition': int,
    'attacker_townhallLevel': int,
    'defender_townhallLevel': int,
    'attack_th_diff': int,
    'defense_th_diff': int,
    'attack_stars': int,
    'attack_percentage': int,
    'attack_duration': int,
    'defender_tag': str,
    'defense_stars': int,
    'defense_percentage': int,
    'defense_duration': int,
    'attacker_tag': str,
    'season': str,
    'battleday': int,
    'wartag': str
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
            'townhallLevel': self._to_int(self.townhallLevel),
            'mapPosition': self._to_int(self.mapPosistion),
            'attacker_townhallLevel': self._to_int(self.attacker_townhallLevel),
            'defender_townhallLevel': self._to_int(self.defender_townhallLevel),
            'attack_th_diff': self._to_int(self.attack_th_diff),  # Positive means attacked higher TH
            'defense_th_diff': self._to_int(self.defense_th_diff),  # Positive means defended against higher TH
            'attack_stars': self._to_int(self.attack_stars),
            'attack_percentage': self._to_int(self.attack_percentage),
            'attack_duration': self._to_int(self.attack_duration),
            'defender_tag': self.defender_tag,
            'defense_stars': self._to_int(self.defense_stars),
            'defense_percentage': self._to_int(self.defense_percentage),
            'defense_duration': self._to_int(self.defense_duration),
            'attacker_tag': self.attacker_tag
        }
    def _to_int(self, value):
        import numpy as np

        # Handle None and "nan" (string)
        if value is None:
            return None
        if isinstance(value, float) and np.isnan(value):
            return None
        if isinstance(value, str):
            val_strip = value.strip("'\"").strip().lower()
            if val_strip == "nan":
                return None
            try:
                return int(float(val_strip))
            except Exception:
                print(f"Warning: Could not convert string value '{value}' to int.")
                return None
        try:
            return int(value)
        except Exception:
            print(f"Warning: Could not convert value '{value}' of type '{type(value)}' to int.")
            return None
               
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
        # print(clan_member)
    assert len(member_array) == len(war_data[Pussay_clan_or_opponent]["members"])

    # Store information in a dataframe
    war_info_df = pd.DataFrame([m.to_dataframe_row() for m in member_array])
    # Add a 'season' column to the DataFrame if 'season' is available in war_data
    season = war_data.get("season", None)
    if season is not None:
        war_info_df["season"] = season
    
    return war_info_df, war_data["state"]

class WarDataManager:
    def __init__(self, status_table="war_status"):
        """
        Initialize the War Data Manager
        
        Args:
            status_table: Table in Supabase tracking war status
        """
        self.status_table = status_table
        
    def get_war_status(self, wartag):
        """
        Get the war status for a specific war tag from Supabase

        Args:
            wartag: The war tag to look up
        Returns:
            dict or None: War status record if found, None otherwise
        """
        war_status = supabase.table(self.status_table).select("*").eq("wartag", wartag).execute().data
        if war_status and len(war_status) > 0:
            # return single record as dict (not a DataFrame) so callers get scalars
            return war_status[0]
        else:
            return None

    def should_load_war(self, wartag):
        """
        Check if a war should be loaded from the API

        Args:
            wartag: The war tag to check

        Returns:
            bool: True if war should be loaded, False if it can be skipped
        """
        # Check if war tag exists in status tracking
        war_status = self.get_war_status(wartag)

        if war_status is None:
            # War not tracked yet, should load
            print(f"War {wartag} not tracked yet. Will load.")
            return True

        loading_status = war_status.get('loading_status')
        coc_status = war_status.get('coc_war_status')

        # skip if loading_status is 'completed'
        if loading_status in ['completed', "Error - too old"]:
            print(f"War {wartag} already marked as '{loading_status}' (COC status: {coc_status}). Skipping.")
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
        elif coc_war_status == "notInWar":
            return "Error - too old"
        else:
            # This shouldn't normally happen, but default to notLoaded
            return "notLoaded"
        
    def clean_record_for_supabase(self, record, schema=WAR_DATA_SCHEMA):
        cleaned = {}
        for key, dtype in schema.items():
            val = record.get(key)
            if dtype is int:
                try:
                    # Handle None, np.nan, and string 'nan'
                    if val is None:
                        cleaned[key] = None
                    elif isinstance(val, float) and (np.isnan(val) or str(val).lower() == "nan"):
                        cleaned[key] = None
                    elif isinstance(val, str) and val.strip().lower() == "nan":
                        cleaned[key] = None
                    else:
                        cleaned[key] = int(float(val))
                except Exception:
                    cleaned[key] = None
            elif dtype is str:
                # Handle None and clean up strings
                if val is None:
                    cleaned[key] = None
                else:
                    cleaned[key] = str(val).strip()
            else:
                cleaned[key] = val
        return cleaned
    
    def save_war_data(self, wartag, war_df, coc_war_status, season, battleday):
            # Add metadata
        war_df['wartag'] = wartag
        war_df['season'] = season
        battleday = int(battleday) if battleday is not None else None
        war_df['battleday'] = battleday

        if war_df is not None and not war_df.empty:
            clean_df = war_df.replace([np.inf, -np.inf], None)
            clean_df = clean_df.map(lambda x: None if pd.isnull(x) else x)

            records = clean_df.to_dict(orient='records')
            if records is None or len(records) == 0:
                raise ValueError(f"No war data records to save for {wartag}.")
            else:
                print(f"Saving {len(records)} war data records for war {wartag}.")
            for record in records:
                record = self.clean_record_for_supabase(record)
                
                if record is None:
                    print(f"Skipping empty record for war {wartag}.")
                    continue

                try:
                    # Check if the row exists (by wartag and tag)
                    query = supabase.table("war_data") \
                        .select("wartag,tag") \
                        .eq("wartag", record["wartag"]) \
                        .eq("tag", record["tag"]) \
                        .execute()
                    exists = query.data and len(query.data) > 0

                    if not exists:
                        print(f"Inserted new war data for {record['tag']} in war {record['wartag']}")
                        # Insert new row
                        res = supabase.table("war_data").insert(record).execute()
                        # optional: print(res) to see DB response
                    else:
                        print(f"Updated war data for {record['tag']} in war {record['wartag']}")
                        # Update existing row
                        response = supabase.table("war_data") \
                            .update(record) \
                            .eq("wartag", record["wartag"]) \
                            .eq("tag", record["tag"]) \
                            .execute()
                    
                    if response.data is None:
                        raise ValueError(f"Supabase response data is None for war data upsert of {record['tag']} in war {record['wartag']}.")
                    # else:
                    #     print(f"inserted/updated {len(response.data)} record(s) for war data of {record['tag']} in war {record['wartag']}.")

                except Exception as e:
                    print(record)
                    raise ValueError(f"Error upserting war data to Supabase: {e}")

        # Upsert war status (this is the critical part)
        try:
            # Check if war_status row exists
            status_query = supabase.table("war_status") \
                .select("id") \
                .eq("wartag", wartag) \
                .execute()
            status_exists = status_query.data and len(status_query.data) > 0

            war_status_record = {
                "wartag": wartag,
                "coc_war_status": coc_war_status,
                "loading_status": loading_status,
                "season": season,
                "battleday": battleday
            }

            if not status_exists:
                print(f"📝 Inserting new war status for {wartag}")
                supabase.table("war_status").insert(war_status_record).execute()
            else:
                print(f"📝 Updating war status for {wartag} → {loading_status}")
                supabase.table("war_status") \
                    .update(war_status_record) \
                    .eq("wartag", wartag) \
                    .execute()

            status_symbol = "✓" if loading_status == "completed" else "⋯"
            if coc_war_status == "notInWar" or loading_status in ["Error - too old", "notLoaded"]:
                print(f"✗ Skipping war {wartag} | Marked as {coc_war_status} ({loading_status}) — will not reload again.")
            else:
                print(f"{status_symbol} Saved war {wartag} | COC war status: {coc_war_status} | Loading: {loading_status}")

        except Exception as e:
            print(f"❌ Error upserting war status for {wartag}: {e}")
    
    def load_cached_war_data(self, wartag):
        """
        Load previously saved war data if available
        
        Args:
            wartag: The war tag
            
        Returns:
            pd.DataFrame or None: War data if available, None otherwise
        """
        
        # Load specific war data from supabase "war_data" table
        war_data = supabase.table("war_data").select("*").eq("wartag", wartag).execute().data
        if war_data:
            return pd.DataFrame(war_data)
        else:
            return None
    
    def process_war(self, wartag, get_war_stats_func, season=None,   battleday=None):
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
            # Try cache — but if none, just return immediately and do NOT call API
            cached_data = self.load_cached_war_data(wartag)
            if cached_data is not None:
                war_status = self.get_war_status(wartag)
                if season is not None and 'season' not in cached_data.columns:
                    cached_data['season'] = season
                if battleday is not None and 'battleday' not in cached_data.columns:
                    cached_data['battleday'] = battleday
                return cached_data, war_status['coc_war_status'], war_status['loading_status'], True
            
            # ✅ NO CACHE — means this war is permanently skipped
            war_status = self.get_war_status(wartag)
            print(f"⚠ No cached data for {wartag} — but it's marked as '{war_status['loading_status']}'. Skipping API call.")
            return pd.DataFrame(), war_status['coc_war_status'], war_status['loading_status'], False

        
        # Load from API
        try:
            war_df, coc_war_status = get_war_stats_func(wartag)

            # Add season and cwl_day columns
            if season is not None:
                war_df['season'] = season
            if battleday is not None:
                war_df['battleday'] = battleday

            war_df['wartag'] = wartag  # Add wartag to DataFrame
            
            # Determine loading status
            loading_status = self.determine_loading_status(coc_war_status)
            
            # Save the data, ensuring season and battleday persist to table
            self.save_war_data(wartag, war_df, coc_war_status, season=season, battleday=battleday)
            
            return war_df, coc_war_status, loading_status, False
            
        except Exception as e:
            print(f"Error loading war {wartag}: {e}")

            # If war is in "notInWar" or too old, mark it as such in `war_status.csv`
            if "notInWar" in str(e) or "too long ago" in str(e):
                self.save_war_data(
                    wartag,
                    war_df=pd.DataFrame(),        # empty since no data
                    coc_war_status="notInWar",  # mark as not available
                    season=season,
                    battleday=battleday
                )
                return pd.DataFrame(), "notInWar", "Error - too old", False


            # Try to return cached data if available
            cached_data = self.load_cached_war_data(wartag)
            if cached_data is not None:
                print(f"⚠ Returning cached data for {wartag} due to API error")
                war_status = self.get_war_status(wartag)
                # Add season and cwl_day if not already present
                if season is not None and 'season' not in cached_data.columns:
                    cached_data['season'] = season
                if battleday is not None and 'battleday' not in cached_data.columns:
                    cached_data['battleday'] = battleday
                return (
                    cached_data,
                    war_status['coc_war_status'],
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
        # Load the latest status data from Supabase
        war_status_data = supabase.table(self.status_table).select("*").execute().data
        status_df = pd.DataFrame(war_status_data) if war_status_data else pd.DataFrame(columns=[
            'wartag', 'coc_war_status', 'loading_status', 'last_updated', 'data_file'
        ])
        if status_df.empty:
            return {
                'total_wars': 0,
                'completed': 0,
                'in_progress': 0,
                'not_loaded': 0
            }
        
        return {
            'total_wars': len(status_df),
            'completed': len(status_df[status_df['loading_status'] == 'completed']),
            'in_progress': len(status_df[status_df['loading_status'] == 'inProgress']),
            'not_loaded': len(status_df[status_df['loading_status'].isin(['notLoaded'])]),
            'too_old': len(status_df[status_df['loading_status'] == 'Error - too old'])
        }
    
    def __repr__(self):
        """Return a formatted summary of war statuses"""
        summary = self.get_status_summary()
        lines = [
            "\n" + "=" * 50,
            "WAR DATA STATUS SUMMARY",
            "=" * 50,
            f"Total Wars Tracked:     {summary['total_wars']}",
            f"✓ Completed:            {summary['completed']}",
            f"⋯ In Progress:          {summary['in_progress']}",
            f"○ Not Loaded:           {summary['not_loaded']}",
            f"✗ Too Old to Load:      {summary['too_old']}",
            "=" * 50 + "\n"
        ]
        return "\n".join(lines)

BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')

def ensure_backup_dir():
    """Create backups directory if it doesn't exist"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    return BACKUP_DIR

def save_war_data_to_csv(all_wars_data, war_status_data):
    """Save war data and status to CSV files for backup"""
    ensure_backup_dir()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save war data
    if all_wars_data:
        combined_df = pd.concat(all_wars_data, ignore_index=True)
        war_data_file = os.path.join(BACKUP_DIR, f'war_data_backup_{timestamp}.csv')
        combined_df.to_csv(war_data_file, index=False)
        print(f"✅ War data backed up to: {war_data_file}")
    
    # Save war status
    if war_status_data:
        status_df = pd.DataFrame(war_status_data)
        status_file = os.path.join(BACKUP_DIR, f'war_status_backup_{timestamp}.csv')
        status_df.to_csv(status_file, index=False)
        print(f"✅ War status backed up to: {status_file}")

def load_warData_supabase():
    # Initialize the manager
    war_manager = WarDataManager(
        status_table="war_status"
    )
    
    # Load your battle tags from supabase
    Pussay_wars = supabase.table("battle_tags").select("*").execute().data
    Pussay_wars_df = pd.DataFrame(Pussay_wars)

    # Process each war
    all_wars_data = []
    
    for idx, row in Pussay_wars_df.iterrows():
        wartag = row['wartag']
        battleday = row['battleday']
        season = row['season']
        
        # Skip placeholder tags
        if wartag == "#0":
            print(f"○ Skipping placeholder war tag for Season {season}, Battle Day {battleday}")
            continue
        
        print(f"\n--- Season {season}, Battle Day {battleday}: {wartag} ---")
        
        try:
            # Process the war (will use cache if completed)
            war_df, coc_status, loading_status, was_cached = war_manager.process_war(
                wartag,
                get_war_stats,  # Your existing code
                season=season,
                battleday=battleday
            )
            
            # Add metadata
            war_df['battleday'] = battleday
            war_df['season'] = season
            war_df['wartag'] = wartag
            
            all_wars_data.append(war_df)
            
            if was_cached:
                print(f"  → Loaded from cache")
            elif coc_status == "notInWar" or loading_status in ["Error - too old", "notLoaded"]:
                pass
            else:
                print(f"  → Fetched from API")
                
        except ValueError as e:
            # Handle "notInWar" or other API errors
            print(f"✗ Could not load war {wartag}: {e}")
            continue
    
    # Print summary
    print(war_manager)
if __name__ == "__main__":
    # load_warData_supabase()
    # Initialize the manager
    war_manager = WarDataManager(
        status_table="war_status"
    )
    
    # Load your battle tags from supabase
    Pussay_wars = supabase.table("battle_tags").select("*").execute().data
    Pussay_wars_df = pd.DataFrame(Pussay_wars)

    # Process each war
    all_wars_data = []
    
    for idx, row in Pussay_wars_df.iterrows():
        wartag = row['wartag']
        battleday = row['battleday']
        season = row['season']
        
        # Skip placeholder tags
        if wartag == "#0":
            print(f"○ Skipping placeholder war tag for Season {season}, Battle Day {battleday}")
            continue
        
        print(f"\n--- Season {season}, Battle Day {battleday}: {wartag} ---")
        
        try:
            # Process the war (will use cache if completed)
            war_df, coc_status, loading_status, was_cached = war_manager.process_war(
                wartag,
                get_war_stats,  # Your existing code
                season=season,
                battleday=battleday
            )
            
            # Add metadata
            war_df['battleday'] = battleday
            war_df['season'] = season
            war_df['wartag'] = wartag
            
            all_wars_data.append(war_df)
            
            if was_cached:
                print(f"  → Loaded from cache")
            elif coc_status == "notInWar" or loading_status in ["Error - too old", "notLoaded"]:
                pass
            else:
                print(f"  → Fetched from API")
                
        except ValueError as e:
            # Handle "notInWar" or other API errors
            print(f"✗ Could not load war {wartag}: {e}")
            continue
    
    # Print summary
    print(war_manager)