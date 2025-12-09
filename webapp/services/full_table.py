from webapp.supabase_client import supabase
import pandas as pd

def get_full_table_data(season_filter=None, player_filter=None):
    
    query = supabase.table("war_data").select("*")
    if player_filter:
        query = query.eq("name", player_filter)
    if season_filter:
        query = query.eq("season", season_filter)
    
    # Execute the query and fetch data
    result = query.execute()
    # Process the data into structured format
    if "error" in result:
        return {"error": result["error"]}  # Return error if query fails
    
    data = pd.DataFrame(result.data)

    # Important columns to display in tables
    important_columns = ["name", "attack_th_diff", "defense_th_diff", "attack_stars", "attack_percentage", "defense_stars", "defense_percentage", "season", "battleday","attack_duration", "defense_duration", "townhallLevel", "mapPosition"]

    # Filter data to only include important columns
    filtered_data = data[important_columns] if not data.empty else pd.DataFrame(columns=important_columns)

    return filtered_data

if __name__ == "__main__":
    # Example usage
    df = get_full_table_data(season_filter="2025-11", player_filter="rozzledog 72")
    print(df.head())

