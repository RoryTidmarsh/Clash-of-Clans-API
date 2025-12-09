# Clash of Clans API - Web Application

This is the **read-only web application** for displaying Clash of Clans war statistics. It fetches data from Supabase and presents it through an interactive Flask-based web interface.

## Architecture

The webapp has been restructured to be **read-only**, meaning:
- ✅ It **reads** war data from Supabase cloud storage
- ✅ It **displays** statistics, tables, and graphs
- ❌ It does **NOT** refresh data from the Clash of Clans API
- ❌ It does **NOT** require CoC API keys

Data refreshing is handled separately by scripts in the `refresh/` folder, designed to run on a Raspberry Pi via cron jobs.

## Project Structure

```
webapp/
├── __init__.py              # Flask app factory
├── routes.py                # Web routes and endpoints
├── supabase_client.py       # Supabase connection (read-only)
├── requirements.txt         # Python dependencies for webapp
├── .env.webapp.example      # Example environment variables
├── services/                # Business logic modules
│   ├── index_data.py        # Homepage data processing
│   ├── full_table.py        # War table data
│   ├── graphs.py            # Graph data processing
│   └── process_data.py      # Data transformation utilities
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── index.html           # Homepage
│   ├── war_data.html        # War data table
│   ├── graphs.html          # Progress graphs
│   └── coming_soon.html     # Coming soon page
└── static/                  # Static assets
    ├── style.css            # Stylesheets
    ├── graphs.js            # Chart.js integration
    ├── filters.js           # Filter controls
    └── components.js        # UI components
```

## Environment Variables

The webapp requires a `.env.webapp` file in the webapp directory with the following variables:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

See `.env.webapp.example` for a template.

**Note**: For read-only access, you can use the Supabase **anon key**. The service key is only needed for the refresh scripts.

## Local Development

1. **Create environment file**:
   ```bash
   cd webapp
   cp .env.webapp.example .env.webapp
   # Edit .env.webapp with your Supabase credentials
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the development server**:
   ```bash
   cd ..  # Back to project root
   python run.py
   ```

4. **Access the application**:
   Open your browser to `http://localhost:5000`

## Production Deployment

For production deployment instructions to Render, see [RENDER_DEPLOYMENT.md](../RENDER_DEPLOYMENT.md) in the root directory.

## Features

- **Homepage**: View recent and all-time player statistics
- **War Table**: Detailed view of all war data with filters
- **Progress Graphs**: Visualize player performance over seasons
- **Player Filters**: Filter data by specific players
- **Season Filters**: View data for specific seasons

## Dependencies

- **Flask 3.0.0**: Web framework
- **gunicorn 21.2.0**: Production WSGI server
- **supabase 2.3.0**: Database client
- **pandas 2.1.4**: Data processing
- **numpy 1.26.2**: Numerical operations
- **python-dotenv 1.0.0**: Environment variable management

## API Endpoints

- `GET /` - Homepage with player statistics
- `GET /war-table` - Full war data table with filters
- `GET /progress-graphs` - Player progress graphs
- `GET /api/graph-data` - API endpoint for dynamic graph data
- `GET /coming-soon` - Coming soon page

## Notes

- The webapp only requires **read access** to Supabase
- No Clash of Clans API keys are needed
- Data refresh is handled separately (see `refresh/` folder)
- All data is cached in Supabase for fast access
