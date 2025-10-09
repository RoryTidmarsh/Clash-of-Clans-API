# Clash of Clans API

Retrieving data from the Clash of Clans API for clan war and clan war league statistics for Pussay Palace.

---

## Project Structure

```plaintext
Clash-of-Clans-API/
│
├── app/                        # Main Flask app package
│   ├── __init__.py             # Flask app setup (app factory)
│   ├── routes.py               # Flask routes/views for web pages
│   ├── supabase_client.py      # Supabase connection & helper functions
│   ├── services/               # Business/data/service logic
│   │   ├── reading_warData.py      # Reads war data from API/Supabase
│   │   ├── Find_battletags.py      # Finds and manages battle tags
│   │   ├── coc_api.py              # Clash of Clans API request helpers
│   │   ├── analysis.py             # Data analysis, graphing, aggregation
│   │   └── ...                     # Additional service/data modules
│   ├── templates/              # Jinja2 HTML templates for the website
│   │   ├── base.html           # Base template for inheritance
│   │   ├── index.html          # Homepage
│   │   ├── war_data.html       # Clan war data table
│   │   ├── graphs.html         # Graphs/visuals
│   │   └── ...                 # Other pages
│   ├── static/                 # Static files (CSS, JS, images)
│   │   ├── images/             # Any images used
│   │   ├── style.css           # Stylesheets
│   │   ├── graphs.js           # JS for charts
│   │   └── ...                 # Additional static assets
│
├── scripts/                    # Standalone scripts for backend jobs
│   ├── refresh_data.py         # Triggers data refresh from CoC API to Supabase
│   ├── generate_graphs.py      # Produces graph data for website
│   └── ...                     # Other admin/data scripts
│
├── .env                        # Environment variables (Supabase, API keys)
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
└── run.py                      # Entry point for running the Flask app
```

---

## File Descriptions

- **app/services/Find_battletags.py**: Creates and manages the battle tag data for all clan war league wars played since the 2025-05 season.
- **app/services/reading_warData.py**: Reads battle tag data and communicates with the Clash of Clans API to retrieve war information for each tag; stores results in Supabase.
- **app/services/analysis.py**: Processes data and generates statistics or data for graphs/tables.
- **scripts/refresh_data.py**: Standalone script that triggers a refresh of data from the Clash of Clans API into Supabase.
- **scripts/generate_graphs.py**: Script to generate graph data, if needed, for website display.
- **app/templates/**: Contains HTML templates for the Flask website, including tables and charts.
- **app/static/**: Contains static assets for frontend (CSS, JS, images).

---

## .env File

This project requires a `.env` file in the root directory to securely store sensitive configuration variables such as API keys, tokens, and other environment-specific settings.

**Values to include in the `.env` file:**
- `SUPABASE_URL`: The URL for your Supabase instance.
- `SUPABASE_SERVICE_KEY`: The API key for your Supabase instance. Supabase updates will only work with a service role.
- `COC_API_KEY`: The API key for accessing the Clash of Clans API.
- Any other secrets or configuration values required by the application.

**Note:**  
Do not commit your `.env` file to version control to keep your credentials secure.

---

## Usage

1. Add your `.env` file with the required keys.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask app:
   ```bash
   python run.py
   ```
4. Access the website in your browser and use the refresh button to update data from the Clash of Clans API.

---

## License

[MIT](LICENSE)