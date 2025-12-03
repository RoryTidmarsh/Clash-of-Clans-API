from flask import Blueprint, render_template, request, jsonify, Response
import app.services.index_data as index_data
import app.services.process_data as process_data
from app.services.Find_battletags import get_war_tags, wars_with_clan, Update_Supabase_battle_tags
import app.services.full_table as full_table
from app.services.reading_WarData import WarDataManager, get_war_stats
import app.services.graphs as graphs
import pandas as pd
import numpy as np
import os
from app.supabase_client import supabase


bp = Blueprint('main', __name__)

def clean_nan_values(data):
    """
    Replace NaN values with None in a list of dictionaries or DataFrame.
    This ensures proper JSON serialization without NaN errors.
    Handles nested structures recursively.
    
    Args:
        data: Either a pandas DataFrame, list, dict, or primitive value
        
    Returns:
        Cleaned data in the same format as input
    """
    if isinstance(data, pd.DataFrame):
        return data.replace({np.nan: None})
    elif isinstance(data, list):
        cleaned_data = []
        for item in data:
            if isinstance(item, dict):
                cleaned_row = {}
                for key, value in item.items():
                    try:
                        # pd.isna() can handle scalar values including numpy types
                        if pd.isna(value) and not isinstance(value, (list, dict)):
                            cleaned_row[key] = None
                        elif isinstance(value, (list, dict)):
                            cleaned_row[key] = clean_nan_values(value)
                        else:
                            cleaned_row[key] = value
                    except (TypeError, ValueError):
                        # If pd.isna() fails (e.g., on complex objects), keep original
                        if isinstance(value, (list, dict)):
                            cleaned_row[key] = clean_nan_values(value)
                        else:
                            cleaned_row[key] = value
                cleaned_data.append(cleaned_row)
            elif isinstance(item, (list, dict)):
                cleaned_data.append(clean_nan_values(item))
            else:
                try:
                    if pd.isna(item):
                        cleaned_data.append(None)
                    else:
                        cleaned_data.append(item)
                except (TypeError, ValueError):
                    cleaned_data.append(item)
        return cleaned_data
    elif isinstance(data, dict):
        cleaned_dict = {}
        for key, value in data.items():
            try:
                if pd.isna(value) and not isinstance(value, (list, dict)):
                    cleaned_dict[key] = None
                elif isinstance(value, (list, dict)):
                    cleaned_dict[key] = clean_nan_values(value)
                else:
                    cleaned_dict[key] = value
            except (TypeError, ValueError):
                if isinstance(value, (list, dict)):
                    cleaned_dict[key] = clean_nan_values(value)
                else:
                    cleaned_dict[key] = value
        return cleaned_dict
    else:
        try:
            if pd.isna(data):
                return None
        except (TypeError, ValueError):
            pass
    return data


@bp.route('/', methods=['GET'])
def index():
    # Get filters from request args
    season_filter = request.args.get("season")  # Get the "season" query parameter, if provided
    player_filter = request.args.get("player")  # Get the "player" query parameter, if provided

    # Fetch raw data
    page_data = index_data.get_index_data(season_filter, player_filter)

    # Translate and reorder columns
    page_data["recent_stats"] = process_data.translate_columns(process_data.reorder_columns(process_data.remove_columns(page_data["recent_stats"], ["season"])))
    page_data["all_time_stats"] = process_data.translate_columns(process_data.reorder_columns(process_data.remove_columns(page_data["all_time_stats"], ["season"])))
    
    # Clean NaN values to avoid JSON parsing errors
    page_data["recent_stats"] = clean_nan_values(page_data["recent_stats"])
    page_data["all_time_stats"] = clean_nan_values(page_data["all_time_stats"])
    
    # print(reorder_columns(page_data["recent_stats"][0]))
    

    # Render the template with translated and reordered column names
    return render_template(
        "index.html",
        filters=page_data["filters"],
        recent_stats=page_data["recent_stats"],
        all_time_stats=page_data["all_time_stats"],
        all_players=index_data.get_all_players(),
    )

@bp.route('/coming-soon', methods=['GET'])
def coming_soon():
    # Simple route for "Coming Soon" page
    return render_template("coming_soon.html")

@bp.route('/war-table', methods=['GET'])
def war_table():
    # Handle multiple players from multi-select dropdown
    selected_players = request.args.getlist("player")  # Get list of selected players
    season_filter = request.args.get("season")  # Get the "season" query parameter, if provided
    
    # Convert list to single value for backward compatibility with existing functions
    if len(selected_players) == 1:
        player_filter = selected_players[0]
    elif len(selected_players) > 1:
        player_filter = selected_players
    else:
        player_filter = None

    war_data = full_table.get_full_table_data(season_filter, player_filter)
    war_data = process_data.translate_columns(process_data.reorder_columns(war_data))
    
    # Convert DataFrame to list of dictionaries for template compatibility
    if isinstance(war_data, pd.DataFrame):
        war_data_list = war_data.to_dict('records')  # Convert to list of dicts
        columns = list(war_data.columns)  # Get column names
    elif isinstance(war_data, list) and len(war_data) > 0:
        war_data_list = war_data
        columns = list(war_data[0].keys()) if war_data else []
    else:
        # Handle empty or unexpected data
        war_data_list = []
        columns = []
    
    # Clean NaN values to avoid JSON parsing errors
    war_data_list = clean_nan_values(war_data_list)
    
    # Debug logging
    print(f"🔍 War table debug:")
    print(f"  - War data type: {type(war_data)}")
    print(f"  - War data length: {len(war_data_list)}")
    print(f"  - Columns: {columns}")
    if war_data_list:
        print(f"  - First row keys: {list(war_data_list[0].keys())}")
    
    # Get all available options for dropdowns
    all_players = index_data.get_all_players()
    all_seasons = index_data.get_all_seasons()

    return render_template("war_data.html",
        war_data=war_data_list,
        columns=columns,
        all_players=all_players,
        all_seasons=all_seasons,
        selected_players=selected_players,
        selected_season=season_filter
    )

@bp.route('/progress-graphs', methods=['GET'])
def progress_graphs():

    # Create filter options for statistic to display
    # stats to drop from available options
    drop_stats = {"tag", "name", "attacker_tag", "defender_tag", "wartag", "battleday", "season", "townhallLevel", "opponent_townhallLevel"}

    # Build available_stats from COLUMNTRANSLATIONS excluding drop_stats
    available_stats = [
        {"value": key, "label": (label or key)}
        for key, label in process_data.COLUMN_TRANSLATIONS.items()
        if key not in drop_stats
    ]
    available_stats.sort(key=process_data.get_priority_index)

    # Fetch all players for filter options
    all_players = index_data.get_all_players()
    print(f"All players for filter: {all_players}")
    # Load the real data
    y_vars = ["attack_stars"] # Default Y variable(s)
    grouped_data, labels = graphs.fetch_graph_data(y_vars, x_variable="season", player_filter=None)

    # trial data for testing
    trial_data = pd.DataFrame({"season": ["2025-09", "2025-10","2025-11","2025-09","2025-11"], "name": ["rozzledog 72","rozzledog 72","rozzledog 72", "conan_1014", 'conan_1014'], "attack_stars": [2.7,2.6,1.65,3.0,1.5]})

    # prepare Chart.js data for the first y variable (or loop if multiple)
    chartjs_data = graphs.prepare_chartjs_data(grouped_data, y_variable=y_vars[0], x_variable="season")
    
    # Clean NaN values to avoid JSON parsing errors
    chartjs_data = clean_nan_values(chartjs_data)
    
    # pass the prepared structure to the template; use Jinja's tojson in template
    return render_template("graphs.html",
                           chartjs_data=chartjs_data,
                           x_label="season",
                           y_label=process_data.COLUMN_TRANSLATIONS.get(y_vars[0]),
                           all_players = all_players,
                           available_stats = available_stats)

@bp.route('/api/graph-data', methods=['GET'])
def get_graph_data():
    """API endpoint to fetch graph data based on query parameters.
    
    ARGS:
        y_vars (list): List of Y variable names to plot.
        x_variable (str): X variable name.
        player_filter (list): List of player names to filter data.
    """
    # Get parameters
    selected_players = request.args.getlist("selected_players")  # List of player names
    selected_stat = request.args.get("stat", "attack_stars")  # Y variable

    print(f"📊 API Request Received:")
    print(f"  - Players: {selected_players}")
    print(f"  - Stat: {selected_stat}")

    try:
        # Fetch and prepare graph data
        grouped_data, labels = graphs.fetch_graph_data(
            y_variables=[selected_stat],
            x_variable="season",
            player_filter=selected_players if selected_players else None
        )

        # Prepare Chart.js data
        chartjs_data = graphs.prepare_chartjs_data(
            grouped_data,
            y_variable=selected_stat,
            x_variable="season"
        )

        return jsonify(chartjs_data)
    
    except Exception as e:
        print(f"❌ Error in API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bp.route('/refresh-data', methods=['POST'])
def refresh_data():
    messages = []
    coc_api_key = os.getenv("COC_API_KEY")
    clan_tag = "%23CQGY2LQU"
    headers = {
        "Accept": "application/json",
        "authorization": "Bearer %s" % coc_api_key
    }  

    seasonal_battle_tag_df, season = get_war_tags(clan_tag, headers)
    messages.append("CWL WAR TAGS FOUND")

    clan_war_tags, clan_war_states = wars_with_clan(seasonal_battle_tag_df)
    messages.append("CLAN ONLY WAR TAGS FOUND")

    reduced_warTag_df = pd.DataFrame(columns=["battleday", "wartag", "season"])
    for day, tag in clan_war_tags.items():
        reduced_warTag_df = pd.concat([reduced_warTag_df, pd.DataFrame({"battleday": [day], "wartag": [tag], "season": [season]})], ignore_index=True)
    # Update Supabase with new war tags
    Update_Supabase_battle_tags(reduced_warTag_df)
    messages.append("SUPABASE BATTLE TAGS UPDATED")

    war_manager = WarDataManager(status_table="war_status")
    total = sum(1 for tag in clan_war_tags.values() if tag != "#0")
    done = 0

    for day, wartag in clan_war_tags.items():
        if wartag == "#0":
            continue
        msg = f"Refreshing war data for: {wartag}, day {day}, season {season}"
        print(msg, flush=True)
        messages.append(msg)

        # Process the war
        war_manager.process_war(
            wartag,
            get_war_stats,
            season=season,
            battleday=day
        )

        # Increment progress and log status
        done += 1
        progress_msg = f"Found data for {done}/{total}"
        print(progress_msg, flush=True)
        messages.append(progress_msg)
    
    messages.append("Data refreshed!")
    return jsonify({"success": True, "message": "Data refreshed!", "log": messages})

@bp.route('/refresh-status')
def refresh_status():
    def event_stream():
        # Imagine these are your steps
        yield "data: Starting refresh...\n\n"
        yield "data: Finding battletags...\n\n"
        # Call Find_battletags function here, yield progress...
        yield "data: Reading war data...\n\n"
        # Call reading_WarData function here, yield progress...
        yield "data: Done!\n\n"
    return Response(event_stream(), mimetype="text/event-stream")