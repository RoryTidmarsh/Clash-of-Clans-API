from app.supabase_client import supabase
import pandas as pd

def get_index_data(player_filter=None):
    """ Get the data for the index page, including recent war stats and all-time stats.
    Args:
        
        player_filter (str, optional): Player name to filter data by.
        
    Returns:
        dict: A dictionary containing recent_stats, all_time_stats, and filters."""
    # Fetch recent war stats & all-time stats from Supabase
    # Define the filters for Supabase query
    query = supabase.table("war_data").select("*")
    if player_filter:
        query = query.eq("name", player_filter)

    # Execute the query and fetch data
    try:
        result = query.execute()
    except Exception as e:
        raise ValueError("error", f"Error fetching data: {e}")  # Return error if query fails

    data_exists = result.data and len(result.data) > 0
    if data_exists:
        lengthData = len(result.data)
    if not data_exists:
        raise ValueError("error", "No data found for the given filters.")
    
    print(f"Fetched {len(result.data)} records from the database.")

    # Process the data into structured format
    if "error" in result:
        raise ValueError("error", f"Error fetching data: {result['error']}")  # Return error if query fails
    
    data = pd.DataFrame(result.data)
    if data_exists:
        if lengthData != data.shape[0]:
            raise ValueError("error", "Data length mismatch after conversion to DataFrame.")
        print(f"Data converted to DataFrame with shape: {data.shape}")
    

    # Filter for the most recent season's data
    most_recent_season = find_mostRecent_season()
    if most_recent_season:
        recent_data = data[data['season'] == most_recent_season]
        if recent_data.empty:
            print(f"No recent data found for season: {most_recent_season} and given player filter: {player_filter}")
    else:
        # Empty because if no seasons found for player filter then no recent data
        recent_data = pd.DataFrame(columns=data.columns)
    
    # Important columns to display in tables
    statCols= ["attack_th_diff", "defense_th_diff", "attack_stars", "attack_percentage", "defense_stars", "defense_percentage"]  

    # Example: Extract recent stats (last battleday) and all-time stats
    recent_stats = calculate_averages_by_player(recent_data, statCols)
    all_time_stats = calculate_averages_by_player(data, statCols)
    seasons = list(data["season"].unique())
    players = list(data["name"].unique())
     
    # Define filters for the dropdowns (static or dynamic)
    filters = {
        "players": players,
        "selected_player": player_filter if player_filter is not None else "All Players"
    }

    if not isinstance(recent_stats, pd.DataFrame) or not isinstance(all_time_stats, pd.DataFrame):
        raise TypeError("Processed stats must be pandas DataFrames.")
    # Return structured data
    return {
        "recent_stats": recent_stats,
        "all_time_stats": all_time_stats,
        "filters": filters
    }

def calculate_averages_by_player(dataset, columns):
        """
        Calculate averages for the specified columns in the dataset grouped by player name.
        Returns a dictionary where each key is the player's name and the value is a dictionary of averaged data.

        Args:
            dataset (pd.DataFrame): The dataset to process.
            columns (list): List of columns to calculate averages for.

        Returns:
            dict: A pandas df with player names as keys and their averaged stats as values.
        """

        # Check we have data and if so then proceed
        if isinstance(dataset, pd.DataFrame) and not dataset.empty:
            # group by name and calculate mean for specified columns
            grouped_df = dataset.groupby("name")[columns].mean(numeric_only=True)
            grouped_df = grouped_df.reset_index() # Reset index to have 'name' as a column
            
            return grouped_df
        else:
            # Return empty DataFrame with specified columns if no data
            columns = ["name"] + columns
            return pd.DataFrame(columns=columns)
   
def find_mostRecent_season():
    response = supabase.table("war_data").select("season").order("season", desc=True).limit(1).execute()
    if response.data:
        return response.data[0]['season']
    return None

def get_all_players():
    """
    Fetch all unique player names from the database
    Returns a list of player names
    """    
    try:
        response = supabase.table('war_data').select('name').execute()
        
        # Extract unique names
        players = list(set([row['name'] for row in response.data]))
        return players
    except Exception as e:
        raise ValueError(f"Error fetching player names: {e}")

def get_all_seasons():
    """
    Fetch all unique seasons from the database
    Returns a list of seasons
    """    
    try:
        response = supabase.table('war_data').select('season').execute()
        
        # Extract unique seasons
        seasons = list(set([row['season'] for row in response.data]))
        return seasons
    except Exception as e:
        raise ValueError(f"Error fetching seasons: {e}")

if __name__ == "__main__":
    season = find_mostRecent_season()
    # data = get_index_data(season_filter=season)

    test_data = pd.DataFrame({
        'name': ['player1', 'player2', 'player1', 'player2'],
        'attack_th_diff': [1, 2, 3, 4],
        'defense_th_diff': [2, 3, 4, 5],
        'attack_stars': [3, 2, 1, 3],
        'attack_percentage': [95.5, 88.0, 76.5, 100.0],
        'defense_stars': [1, 2, 3, 0],
        'defense_percentage': [50.0, 60.0, 70.0, 80.0],
        'season': ['2025-11', '2025-11', '2025-10', '2025-11'],
        'poo_stats': [999, 999, 999, 999]
    })
    
    print("Test Data:")
    print(test_data)

    statCols= ["attack_th_diff", "defense_th_diff", "attack_stars", "attack_percentage", "defense_stars", "defense_percentage"]
    averages = calculate_averages_by_player(test_data, statCols)
    print("\nAverages by Player:")
    print(averages)

    assert isinstance(averages, pd.DataFrame)
    assert 'name' in averages.columns
    assert averages.loc[averages['name']== 'player1', 'attack_th_diff'].values[0] == 2.0
    assert averages.loc[averages['name']== 'player2', 'defense_percentage'].values[0] == 70.0
    assert calculate_averages_by_player(pd.DataFrame(), statCols).columns.tolist() == calculate_averages_by_player(test_data, statCols).columns.tolist()
    # print(f"Recent stats for season {season}: \n{type(data['recent_stats'])} \n{data['recent_stats'][0]}")

    print("Players:", get_all_players())
    print("Seasons:", get_all_seasons())

    dictionary = get_index_data(player_filter="conan_1014")
    assert isinstance(dictionary, dict)
    assert dictionary.keys() == {"recent_stats", "all_time_stats", "filters"}

    recent_data = dictionary["recent_stats"]
    all_time_data = dictionary["all_time_stats"]
    filters = dictionary["filters"]

    assert isinstance(recent_data, pd.DataFrame)
    assert isinstance(all_time_data, pd.DataFrame)
    assert isinstance(filters, dict)
    print("\nRecent Data:")
    print(all_time_data)