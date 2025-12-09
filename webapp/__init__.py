from flask import Flask

def create_app():
    webapp = Flask(__name__)

    # Import and register your blueprint (routes)
    from webapp.routes import bp as main_bp
    webapp.register_blueprint(main_bp)
    # You can add further app configuration here (database, extensions, etc.)

    return webapp