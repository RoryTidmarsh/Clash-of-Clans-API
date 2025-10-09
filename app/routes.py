from flask import Blueprint, render_template, request
# from app.services.analysis import get_clan_progress, get_war_table, get_progress_graph_data
from app.supabase_client import supabase

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    # Get filters from request args (e.g., season, player, war type)
    filters = {
        "season": request.args.get("season"),
        "player": request.args.get("player"),
        # Add more filters as needed
    }
    # Fetch recent war stats & all-time stats
    recent_stats, all_time_stats = get_clan_progress(filters)
    return render_template(
        "index.html",
        recent_stats=recent_stats,
        all_time_stats=all_time_stats,
        filters=filters
    )

@bp.route('/war_table', methods=['GET'])
def war_table():
    # Get filters from request args
    filters = {
        "season": request.args.get("season"),
        "player": request.args.get("player"),
        "day": request.args.get("day"),
        # Add more filters as needed
    }
    war_data = get_war_table(filters)
    return render_template(
        "war_data.html",
        war_data=war_data,
        filters=filters
    )

@bp.route('/progress_graphs', methods=['GET'])
def progress_graphs():
    # Get chosen stat and filters from request args
    stat = request.args.get("stat", "stars")
    filters = {
        "season": request.args.get("season"),
        "player": request.args.get("player"),
        # Add more filters as needed
    }
    graph_data = get_progress_graph_data(stat, filters)
    return render_template(
        "graphs.html",
        stat=stat,
        graph_data=graph_data,
        filters=filters
    )