from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import and register your blueprint (routes)
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # You can add further app configuration here (database, extensions, etc.)

    return app