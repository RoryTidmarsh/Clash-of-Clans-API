# Data Refresh Scripts

This folder contains the scripts used to **refresh war data** from the Clash of Clans API and store it in Supabase. These scripts are designed to run separately from the web application, typically on a Raspberry Pi via cron jobs.

## Architecture Separation

The project is split into two parts:
1. **Web Application** (`webapp/` folder): Read-only, displays data from Supabase
2. **Data Refresh Scripts** (this folder): Writes data to Supabase from CoC API

## Purpose

These scripts:
- ✅ Fetch war data from the Clash of Clans API
- ✅ Process and store data in Supabase
- ✅ Update battle tags and war statistics
- ✅ Require CoC API keys and Supabase service key

## Security Note

⚠️ **DO NOT** commit the `.env` file to GitHub!

This folder requires a `.env` file with **service-level** credentials:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_KEY`: Your Supabase **service role** key (NOT the anon key)
- `COC_API_KEY`: Your Clash of Clans API key

The service key is required because these scripts need **write access** to Supabase.

## Files

- `Find_battletags.py`: Discovers and manages battle tags for clan war league wars
- `reading_WarData.py`: Retrieves war information from CoC API for each battle tag
- `supabaseRefresh.py`: Manages Supabase data updates
- `COC_client.py`: Handles Clash of Clans API requests
- `requirements.txt`: Python dependencies for refresh scripts

## Dependencies

See `requirements.txt` for required packages:
- supabase
- pandas
- numpy
- requests
- python-dotenv

## Usage (Raspberry Pi Cron Job)

1. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up cron job** (example):
   ```bash
   # Run data refresh daily at 2 AM
   0 2 * * * cd /path/to/refresh && python supabaseRefresh.py
   ```

## Deployment Note

These scripts should **NOT** be deployed with the web application. They are meant to run independently on a separate system (e.g., Raspberry Pi) with scheduled execution. 