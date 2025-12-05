from flask import Blueprint, render_template, request, jsonify, Response
import app.services.index_data as ID
import app.services.process_data as PD
from app.services.Find_battletags import get_war_tags, wars_with_clan, Update_Supabase_battle_tags
import app.services.full_table as full_table
from app.services.reading_WarData import WarDataManager, get_war_stats
import app.services.graphs as graphs
import pandas as pd
import numpy as np
import os
from app.supabase_client import supabase


bp = Blueprint('main', __name__)




@bp.route('/', methods=['GET'])
def index():
    # Get filters from request args
    player_filter = request.args.get("player")  # Get the "player" query parameter, if provided

    # Fetch raw data
    page_data = ID.get_index_data(player_filter)

    # Translate and reorder columns
    recent_data = page_data["recent_stats"]
    all_time_data = page_data["all_time_stats"]
    filters = page_data["filters"]
    
    # Process data to correct columns, order and translations
    recent_data = PD.process_data(recent_data)
    all_time_data = PD.process_data(all_time_data)

    assert isinstance(recent_data, pd.DataFrame)
    assert isinstance(all_time_data, pd.DataFrame)

    # extract column names - required in Pandas to get cols
    recent_colunmns = list(recent_data.columns)
    all_time_columns = list(all_time_data.columns)

    # Convert DataFrames to JSON-compatible format
    recent_data = PD.Pandas_to_Json(recent_data)
    all_time_data = PD.Pandas_to_Json(all_time_data)
    assert isinstance(recent_data, str)
    assert isinstance(all_time_data, str)

    # Render the template with translated and reordered column names
    return render_template(
        "index.html",
        filters=filters,
        recent_stats=recent_data,
        all_time_stats=all_time_data,
        recent_columns=recent_colunmns,
        all_time_columns=all_time_columns,
        all_players=ID.get_all_players(),
    )

@bp.route('/coming-soon', methods=['GET'])
def coming_soon():
    # Simple route for "Coming Soon" page
    return render_template("coming_soon.html")

@bp.route('/war-table', methods=['GET'])
def war_table():
    # Handle multiple players from multi-select dropdown
    selected_players = request.args.getlist("player")  # Get list of selected players
    season_filter = request.args.getlist("season")  # Get the "season" query parameter, if provided
    
    # Convert list to single value for backward compatibility with existing functions
    if len(selected_players) == 1:
        player_filter = selected_players[0]
    elif len(selected_players) > 1:
        player_filter = selected_players
    else:
        player_filter = None

    war_data = full_table.get_full_table_data(season_filter, player_filter)
    assert isinstance(war_data, pd.DataFrame)
    war_data = PD.replace_nan(PD.translate_columns(PD.reorder_columns(war_data)))
    assert isinstance(war_data, pd.DataFrame)
    columns = list(war_data.columns)

    # Convert to JSON-compatible format
    war_data_JSON = PD.Pandas_to_Json(war_data)
    
    # Debug logging
    print(f"🔍 War table debug:")
    print(f"  - War data type: {type(war_data)}")
    print(f"  - War data length: {len(war_data_JSON)}")
    print(f"  - Columns: {columns}")
    
    # Get all available options for dropdowns
    all_players = ID.get_all_players()
    all_seasons = ID.get_all_seasons()

    return render_template("war_data.html",
        war_data=war_data_JSON,
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
        for key, label in PD.COLUMN_TRANSLATIONS.items()
        if key not in drop_stats
    ]
    available_stats.sort(key=PD.get_priority_index)

    # Fetch all players for filter options
    all_players = ID.get_all_players()
    
    # Load the real data
    y_vars = ["attack_stars"] # Default Y variable(s)
    grouped_data, labels = graphs.fetch_graph_data(y_vars, x_variable="season", player_filter=None)

    # prepare Chart.js data for the first y variable (or loop if multiple)
    chartjs_data = graphs.prepare_chartjs_data(grouped_data, y_variable=y_vars[0], x_variable="season")
    
    # Convert to JSON-compatible format
    chartjs_data =  PD.Pandas_to_Json(chartjs_data)
    
    # pass the prepared structure to the template; use Jinja's tojson in template
    return render_template("graphs.html",
                           chartjs_data=chartjs_data,
                           x_label="season",
                           y_label=PD.COLUMN_TRANSLATIONS.get(y_vars[0]),
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