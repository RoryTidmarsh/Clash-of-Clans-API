# Clash of Clans API

A web application for displaying Clash of Clans war and clan war league statistics for Pussay Palace. The project uses Supabase for cloud data storage and is split into two components: a read-only web application and separate data refresh scripts.

## Architecture Overview

This project has been restructured into two independent components:

### 1. **Web Application** (`webapp/` folder)
- **Purpose**: Read-only web interface for displaying war statistics
- **Deployment**: Designed for cloud hosting (e.g., Render)
- **Database Access**: Read-only access to Supabase (uses anon key)
- **Features**: Interactive tables, graphs, and player statistics
- **No API Keys**: Does not require Clash of Clans API keys

### 2. **Data Refresh Scripts** (`refresh/` folder)
- **Purpose**: Fetch and update war data from Clash of Clans API
- **Deployment**: Designed for Raspberry Pi with cron jobs
- **Database Access**: Write access to Supabase (uses service key)
- **Features**: Automated data collection and storage
- **Requires API Keys**: Needs both CoC API key and Supabase service key

---

## Project Structure

```plaintext
Clash-of-Clans-API/
│
├── webapp/                     # Web application (read-only)
│   ├── __init__.py             # Flask app factory
│   ├── routes.py               # Web routes and API endpoints
│   ├── supabase_client.py      # Supabase read-only connection
│   ├── requirements.txt        # Web app dependencies
│   ├── README.md               # Web app documentation
│   ├── .env.webapp.example     # Example environment variables
│   ├── services/               # Business logic modules
│   │   ├── index_data.py       # Homepage data processing
│   │   ├── full_table.py       # War table data
│   │   ├── graphs.py           # Graph data processing
│   │   └── process_data.py     # Data transformation utilities
│   ├── templates/              # Jinja2 HTML templates
│   │   ├── base.html           # Base template for inheritance
│   │   ├── index.html          # Homepage
│   │   ├── war_data.html       # Clan war data table
│   │   ├── graphs.html         # Progress graphs
│   │   └── coming_soon.html    # Coming soon page
│   └── static/                 # Static files (CSS, JS)
│       ├── style.css           # Stylesheets
│       ├── graphs.js           # Chart.js integration
│       ├── filters.js          # Filter controls
│       └── components.js       # UI components
│
├── refresh/                    # Data refresh scripts (Raspberry Pi)
│   ├── Find_battletags.py      # Battle tag discovery
│   ├── reading_WarData.py      # War data retrieval
│   ├── supabaseRefresh.py      # Supabase data updates
│   ├── COC_client.py           # CoC API client
│   ├── requirements.txt        # Refresh script dependencies
│   └── README.MD               # Refresh scripts documentation
│
├── run.py                      # Flask app entry point
├── README.md                   # This file
├── RENDER_DEPLOYMENT.md        # Render deployment guide
└── .gitignore                  # Git ignore rules
```

---


## Quick Start

### Web Application (Local Development)

1. **Navigate to webapp directory**:
   ```bash
   cd webapp
   ```

2. **Set up environment**:
   ```bash
   cp .env.webapp.example .env.webapp
   # Edit .env.webapp with your Supabase URL and anon key
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   cd ..  # Back to project root
   python run.py
   ```

5. **Access the website**:
   Open your browser to `http://localhost:5000`

### Data Refresh Scripts (Raspberry Pi)

See [refresh/README.MD](refresh/README.MD) for setup instructions.

---

## Environment Variables

### Web Application (.env.webapp)
Located in the `webapp/` directory:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key (read-only access)

### Refresh Scripts (.env)
Located in the `refresh/` directory:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Your Supabase service key (write access)
- `COC_API_KEY`: Your Clash of Clans API key

⚠️ **Security**: Never commit `.env` files to version control! Example files are provided (`.env.webapp.example`).

---

## Deployment

### Production Web Application
For deploying the web application to Render, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for detailed instructions.

### Data Refresh on Raspberry Pi
The refresh scripts should be set up as cron jobs on a Raspberry Pi. See [refresh/README.MD](refresh/README.MD) for details.

---

## Features

- **Interactive Statistics Dashboard**: View player performance metrics
- **War Data Tables**: Detailed war information with filtering
- **Progress Graphs**: Visualize player progress over seasons
- **Player Filtering**: Focus on specific player statistics
- **Season Filtering**: View data for specific CWL seasons
- **Responsive Design**: Works on desktop and mobile devices

---

## License

[MIT](LICENSE)