from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET'])
def index():
    # Placeholder data for testing the index page
    filters = {
        "seasons": ["Spring 2025", "Summer 2025"],
        "players": ["Player1", "Player2"],
        "selected_season": "Spring 2025",
        "selected_player": "Player1"
    }
    recent_stats = [
        {"name": "Placeholder Stat 1", "attack": "Placeholder Attack", "defense": "Placeholder Defense"},
        {"name": "Placeholder Stat 2", "attack": "Placeholder Attack", "defense": "Placeholder Defense"}
    ]
    all_time_stats = [
        {"name": "Placeholder Stat 1", "attack": "Placeholder Attack", "defense": "Placeholder Defense"},
        {"name": "Placeholder Stat 2", "attack": "Placeholder Attack", "defense": "Placeholder Defense"}
    ]
    return render_template(
        "index.html",
        filters=filters,
        recent_stats=recent_stats,
        all_time_stats=all_time_stats
    )

@bp.route('/coming-soon', methods=['GET'])
def coming_soon():
    # Simple route for "Coming Soon" page
    return render_template("coming_soon.html")