from app.supabase_client import supabase
import pandas as pd

def get_index_data(season_filter=None, player_filter=None):
    # Fetch recent war stats & all-time stats from Supabase
    # Define the filters for Supabase query
    query = supabase.table("war_data").select("*")
    if season_filter:
        query = query.eq("season", season_filter)
    if player_filter:
        query = query.eq("name", player_filter)

    # Execute the query and fetch data
    result = query.execute()

    # Process the data into structured format
    if "error" in result:
        return {"error": result["error"]}  # Return error if query fails
    
    data = pd.DataFrame(result.data)
    

    # Filter for the most recent season's data
    most_recent_season = find_mostRecent_season()
    if most_recent_season:
        recent_data = data[data['season'] == most_recent_season]
    else:
        recent_data = []
    
    # Important columns to display in tables
    important_columns = ["name", "attack_th_diff", "defense_th_diff", "attack_stars", "attack_percentage", "defense_stars", "defense_percentage", "season"]

    def calculate_averages_by_player(dataset, columns = important_columns):
        """
        Calculate averages for the specified columns in the dataset grouped by player name.
        Returns a dictionary where each key is the player's name and the value is a dictionary of averaged data.

        Args:
            dataset (pd.DataFrame): The dataset to process.
            columns (list): List of columns to calculate averages for.

        Returns:
            dict: A dictionary with player names as keys and their averaged stats as values.
        """
        averages = {}

        if isinstance(dataset, pd.DataFrame) and not dataset.empty:
            grouped = dataset.groupby("name")
            for name, group in grouped:
                avg_data = {}
                for col in columns:
                    if col in group.columns and pd.api.types.is_numeric_dtype(group[col]):
                        avg_data[col] = round(group[col].mean(), 2)
                    elif col in group.columns:
                        avg_data[col] = group[col].iloc[0]  # Non-numeric columns, take first value
                averages[name] = avg_data
        # re format into a pandas dataframe for easier rendering in template# Translate column names to user-friendly names
    
        averages = pd.DataFrame.from_dict(averages, orient='index').reset_index().rename(columns={"index": "name"})

        #drop one of the "name" columns if it exists
        if "name" in averages.columns and "name" in averages.columns[1:]:
            averages = averages.loc[:,~averages.columns.duplicated()]
        
        return averages
    

    # Example: Extract recent stats (last battleday) and all-time stats
    recent_stats = calculate_averages_by_player(recent_data, important_columns)
    all_time_stats = calculate_averages_by_player(data, important_columns)

    seasons = list(data["season"].unique())
    players = list(data["name"].unique())
     
    # Define filters for the dropdowns (static or dynamic)
    filters = {
        "seasons": seasons,
        "players": players,
        "selected_season": season_filter if season_filter is not None else "All Seasons",
        "selected_player": player_filter if player_filter is not None else "All Players"
    }

    recent_stats = recent_stats.to_dict(orient='records')
    all_time_stats = all_time_stats.to_dict(orient='records')

    # Return structured data
    return {
        "recent_stats": recent_stats,
        "all_time_stats": all_time_stats,
        "filters": filters
    }
    
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


if __name__ == "__main__":
    season = find_mostRecent_season()
    data = get_index_data(season_filter=season)
    
    print(f"Recent stats for season {season}: \n{type(data['recent_stats'])} \n{data['recent_stats'][0]}")

    print("Players:", get_all_players())