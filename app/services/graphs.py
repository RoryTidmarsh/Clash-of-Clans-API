""" This module handles graph-related functionalities. Pulling data from Supabase and preparing it for graphing in `graphs.html`. 
"""
from app.supabase_client import supabase
import pandas as pd
import numpy as np

def fetch_graph_data(y_variables, x_variable="season", player_filter=None):
    """
    Fetches data from Supabase and prepares it for graphing.

    Args:
        y_variables (list): List of Y-axis variables to plot.
        x_variable (str): X-axis variable to plot. Default is "season".
        player_filter (array or list): Filter data for specific player. Defaults to None.

    Returns:
        dict: A dictionary containing the processed data for graphing.
    """        
    
    # Define the filters for Supabase query
    query = supabase.table("war_data").select("*")
    
    query = query.in_("name", player_filter) if player_filter else query
        

    # Execute the query and fetch data
    result = query.execute()

    if len(result.data)==0:
        raise Exception(f"Error fetching data: {result}, double check the filters")  # Raise error if query fails
    
    data = pd.DataFrame(result.data)
    
    # Ensure x_variable and y_variables are in the DataFrame
    if x_variable not in data.columns or not all(var in data.columns for var in y_variables):
        # print(data.columns)
        raise  ValueError(f"Invalid x_variable or y_variables")

    # Data for each player grouped by the x_variable
    grouped_data = data.groupby([x_variable] + ["name"])[y_variables].mean().reset_index()
    grouped_data = grouped_data.sort_values(by=[x_variable, "name"])

    # Prepare data for graphing
    labels = {
        "x_label": grouped_data[x_variable].tolist(),
        "y_label": {var: grouped_data[var].tolist() for var in y_variables}
    }
    
    return grouped_data, labels


if __name__ == "__main__":
    # Example usage
    y_vars = ["attack_stars", "defense_stars"]
    graph_data, labels = fetch_graph_data(y_vars, x_variable="season", player_filter = ["rozzledog 72", "conan_1014"])

    graph_data, labels = fetch_graph_data(["attack_stars"], "season", player_filter = ["rozzledog 72", "conan_1014"])
    print(graph_data.tolist())