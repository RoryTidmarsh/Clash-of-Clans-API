import os
from webapp import create_app

app = create_app()

if __name__ == "__main__":
    # Use environment variables for production deployment
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)

    # app.run(debug=True)