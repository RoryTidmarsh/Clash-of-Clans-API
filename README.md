# Clash of Clans API
 Retrieving data from the clash of clans api, for clan war and clan war league statistics for pussay palace

- `Find_battletags.py`: Creates the `battletags.csv` and `Pussay_battle_tags.csv` file containing the battletags of all clan war league wars played by the clan since the 2025-05 season.
- `reading_WarData.py`: Reads the `Pussay_battle_tags.csv` file and comminicates with the COC api to retrieve the war information for each battletag. The data for each season is stored in the `Seasons Data` directory. 
- `Seasons Data`: Contains files `Pussay_season_data_{season}.csv` for each season. Each file contains the attack and defense data for each player and each battleday in the clan war league season.

.env file description:
This project requires a `.env` file in the root directory to securely store sensitive configuration variables such as API keys, tokens, and other environment-specific settings. 
Values to include in the `.env` file:
- `SUPABASE_URL`: The URL for your Supabase instance.
- `SUPABASE_KEY`: The API key for your Supabase instance.
- `COC_API_KEY`: The API key for accessing the Clash of Clans API.
- Any other secrets or configuration values required by the application.

**Note:** Do not commit your `.env` file to version control to keep your credentials secure.
