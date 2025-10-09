from flask import Blueprint, render_template, request
from app.services.index_data import get_index_data
# from app.services.analysis import get_clan_progress, get_war_table, get_progress_graph_data
from app.supabase_client import supabase

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    # Get filters from request args (e.g., season, player)
    season_filter = request.args.get("season")
    player_filter = request.args.get("player")

    # Fetch data using the service function
    page_data = get_index_data(season_filter, player_filter)

    # Check for errors
    if "error" in page_data:
        return f"Error fetching data: {page_data['error']}", 500

    # Pass the data to the template
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