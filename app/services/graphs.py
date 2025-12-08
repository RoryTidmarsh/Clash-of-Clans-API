""" This module handles graph-related functionalities. Pulling data from Supabase and preparing it for graphing in `graphs.html`. 
"""
from app.supabase_client import supabase
import pandas as pd
import numpy as np
from app.services.process_data import replace_nan, COLUMN_TRANSLATIONS

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

    y_labels = {var: grouped_data[var].tolist() for var in y_variables} 
    # Nan handling: replace NaN with None for JSON compatibility
    grouped_data = replace_nan(grouped_data)

    # Prepare data for graphing
    labels = {
        "x_label": grouped_data[x_variable].tolist(),
        "y_label": {var: grouped_data[var].tolist() for var in y_variables}
    }
    
    return grouped_data, labels

def prepare_chartjs_data(grouped_data, y_variable, x_variable = "season", colours = None):
    """
    Prepares data in a format suitable for Chart.js.

    Args:
        grouped_data (DataFrame): The grouped data containing x and y variables.
        y_variable (str): The Y-axis variable to plot.
        x_variable (str): The X-axis variable to plot. Default is "season".
        colours (list): List of colours for each player. Defaults to None.

    Returns:
        dict: A dictionary formatted for Chart.js consumption.
    """
    if x_variable not in grouped_data.columns:
        raise ValueError(f"x_variable '{x_variable}' not in data columns")
    if y_variable not in grouped_data.columns:
        raise ValueError(f"y_variable '{y_variable}' not in data columns")
    if grouped_data.empty:
        raise ValueError("grouped_data is empty")

    # Get unique x labels
    x_labels = sorted(grouped_data[x_variable].unique())
    print("Step 1 - X Labels:", x_labels)
    # Unique player names
    player_names = grouped_data["name"].unique()
    print("Step 2 - Players:", player_names)
    
    # Colour pallette for multiple lines
    if colours is None:
        colours = [
            "#6d6ed6",  # Purple (your theme color)
            "#51cf66",  # Green
            "#f06595",  # Pink
            "#a993fe",  # Light purple
            "#ff6b6b",  # Red
            "#339af0",  # Blue
            "#4c4cab",  # Darker purple
            "#ff922b",  # Orange
            
        ]

    markers = ['circle','star','cross','triangle', 'rect',  'diamond', 'plus', 'heart']
    
    datasets = []
    for i, player in enumerate(player_names):
        # Fileter data for current player
        player_data = replace_nan(grouped_data[grouped_data["name"]==player])

        # access data into dictionary form
        season_value_map = dict(zip(player_data["season"], player_data[y_variable]))        # in form {"seaon": y_value,...}

        # Handle missing data and aligning with x_labels
        data_values = []
        for ind,season in enumerate(x_labels):
            value = season_value_map.get(season,None)
            if value is None:
                data_values.append(None)
            else:
                try:
                    data_values.append(float("{:.3g}".format(float(value))))
                except (ValueError, TypeError):
                    data_values.append(None)

        # Cycle through colours; when we wrap to a new colour-set (cycle), change markers.
        cycle = i // len(colours)
        colour_index = i % len(colours)
        colour = colours[colour_index]
        # Shift marker selection by the cycle number so each colour-cycle uses a different marker set
        marker = markers[cycle % len(markers)]
        dataset = {
            "label": player, # Player name for legend
            "data": data_values, # Y-axis values aligned with x_labels
            "borderColor": colour, # Line color
            "backgroundColor": colour, # Point fill color (not transparent)
            "pointStyle": marker,  # Marker style
            "pointBackgroundColor": colour, # Explicit point color
            "pointBorderWidth": 2, # Border width around points
            "fill": False, # No fill under the line
            "tension": 0.1, # Smooth curves
            "pointRadius": 6, # Larger point size (was 4)
            "pointHoverRadius": 8, # Larger on hover (was 6)
            "pointHitRadius": 10, # Larger click area
            "spanGaps": False  # Do not connect gaps in data
        }

        datasets.append(dataset)
    
    chartjs_data = {
        "labels": x_labels,
        "datasets": datasets,
        "yLabel": COLUMN_TRANSLATIONS.get(y_variable, y_variable)  # Translate y_variable for axis label
    }
    return chartjs_data
            


if __name__ == "__main__":
    # Example usage
    y_vars = ["attack_stars", "defense_stars"]
    graph_data, labels = fetch_graph_data(y_vars, x_variable="season", player_filter = ["rozzledog 72", "conan_1014"])

    graph_data, labels = fetch_graph_data(["attack_stars"], "season", player_filter = ["rozzledog 72", "conan_1014"])
    

    trial_data = pd.DataFrame({"season": ["2025-09", "2025-10","2025-11","2025-09","2025-11"], "name": ["rozzledog 72","rozzledog 72","rozzledog 72", "conan_1014", 'conan_1014'], "attack_stars": [2.7,2.6,1.65,3.0,1.5]})
    # print(trial_data)
    chartjs_data = prepare_chartjs_data(trial_data, "attack_stars")
    print(chartjs_data)

    print("\nLabels:")
    print(prepare_chartjs_data(graph_data, y_variable=y_vars[0], x_variable="season")["labels"])