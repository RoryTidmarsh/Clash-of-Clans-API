from flask import Blueprint, render_template, request
from app.services.index_data import get_index_data
from app.services.process_data import translate_columns, remove_columns
# from app.services.analysis import get_clan_progress, get_war_table, get_progress_graph_data
from app.supabase_client import supabase

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    # Get filters from request args
    season_filter = request.args.get("season")  # Get the "season" query parameter, if provided
    player_filter = request.args.get("player")  # Get the "player" query parameter, if provided

    # Fetch raw data
    page_data = get_index_data(season_filter, player_filter)

    # Translate and reorder columns
    page_data["recent_stats"] = translate_columns(remove_columns(page_data["recent_stats"], ["season"]))
    page_data["all_time_stats"] = translate_columns(remove_columns(page_data["all_time_stats"], ["season"]))
    
    

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
    # Placeholder route for progress graphs page
    graph_data = {
        "labels": ["January", "February", "March"],
        "values": [10, 20, 30]
    }
    return render_template("progress_graphs.html", graph_data=graph_data)