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
    
    data = result.data

    most_recent_season = find_mostRecent_season()
    if most_recent_season:
        recent_data = [entry for entry in data if entry.get("season") == most_recent_season]
    else:
        recent_data = []

    # Important columns to display in tables
    important_columns = ["name", "attack_th_diff", "defense_th_diff", "attack_stars", "attack_percentage", "defense_stars", "defense_percentage"]

    def calculate_averages_by_player(dataset, columns):
        """
        Calculate averages for the specified columns in the dataset grouped by player name.
        Returns a dictionary where each key is the player's name and the value is a dictionary of averaged data.
        """
        averages = {}

        # Group data by player name
        players = set(entry["name"] for entry in dataset if entry.get("name"))
        for player in players:
            # Filter data for the current player
            player_data = [entry for entry in dataset if entry.get("name") == player]

            # Calculate averages for the specified columns
            player_averages = {}
            for column in columns:
                if column == "name":
                    continue  # Skip the name column
                values = [entry[column] for entry in player_data if entry.get(column) is not None]
                average = sum(values) / len(values) if values else 0
                player_averages[column] = average

            # Store the result for the player
            averages[player] = player_averages

        return averages

    # Example: Extract recent stats (last battleday) and all-time stats
    recent_stats = calculate_averages_by_player(recent_data, important_columns)
    all_time_stats = calculate_averages_by_player(data, important_columns)

    # Define filters for the dropdowns (static or dynamic)
    filters = {
        "seasons": list(set(entry["season"] for entry in data if entry.get("season"))),
        "players": list(set(entry["name"] for entry in data if entry.get("name"))),
        "selected_season": season_filter or "All Seasons",
        "selected_player": player_filter or "All Players"
    }

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


if __name__ == "__main__":
    season = find_mostRecent_season()
    data = get_index_data(season_filter=season)
    print(data)