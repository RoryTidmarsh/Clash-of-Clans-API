from flask import Blueprint, render_template, request, jsonify, Response
from app.services.index_data import get_index_data
from app.services.process_data import translate_columns, remove_columns,reorder_columns
from app.services.Find_battletags import get_war_tags, wars_with_clan, Update_Supabase_battle_tags
from app.services.reading_WarData import WarDataManager, get_war_stats
import app.services.graphs as graphs
import pandas as pd
import os
from app.supabase_client import supabase
import json

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    # Get filters from request args
    season_filter = request.args.get("season")  # Get the "season" query parameter, if provided
    player_filter = request.args.get("player")  # Get the "player" query parameter, if provided

    # Fetch raw data
    page_data = get_index_data(season_filter, player_filter)

    # Translate and reorder columns
    page_data["recent_stats"] = translate_columns(reorder_columns(remove_columns(page_data["recent_stats"], ["season"])))
    page_data["all_time_stats"] = translate_columns(reorder_columns(remove_columns(page_data["all_time_stats"], ["season"])))
    
    # print(reorder_columns(page_data["recent_stats"][0]))
    

    # Render the template with translated and reordered column names
    return render_template(
        "index.html",
        filters=page_data["filters"],
        recent_stats=page_data["recent_stats"],
        all_time_stats=page_data["all_time_stats"]
    )

@bp.route('/coming-soon', methods=['GET'])
def coming_soon():
    # Simple route for "Coming Soon" page
    return render_template("coming_soon.html")

@bp.route('/war-table', methods=['GET'])
def war_table():
    # Placeholder route for war table page
    war_data = [
        {"name": "War Data 1", "detail": "Details about War Data 1"},
        {"name": "War Data 2", "detail": "Details about War Data 2"}
    ]
    return render_template("war_table.html", war_data=war_data)

@bp.route('/progress-graphs', methods=['GET'])
def progress_graphs():
    # Example: one Y variable and optional player filter
    y_vars = ["attack_stars"]
    grouped_data, labels = graphs.fetch_graph_data(y_vars, x_variable="season", player_filter=None)

    trial_data = pd.DataFrame({"season": ["2025-09", "2025-10","2025-11","2025-09","2025-11"], "name": ["rozzledog 72","rozzledog 72","rozzledog 72", "conan_1014", 'conan_1014'], "attack_stars": [2.7,2.6,1.65,3.0,1.5]})

    # prepare Chart.js data for the first y variable (or loop if multiple)
    chartjs_data = graphs.prepare_chartjs_data(trial_data, y_variable=y_vars[0], x_variable="season")
    print("📊 Sending to template:", chartjs_data)  # Debug print
    # pass the prepared structure to the template; use Jinja's tojson in template
    return render_template("graphs.html",
                           chartjs_data=chartjs_data,
                           x_label="season",
                           y_label=y_vars[0])

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