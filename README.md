# Clash of Clans API
 Retrieving data from the clash of clans api, for clan war and clan war league statistics for pussay palace

- `Find_battletags.py`: Creates the `battletags.csv` and `Pussay_battle_tags.csv` file containing the battletags of all clan war league wars played by the clan since the 2025-05 season.
- `reading_WarData.py`: Reads the `Pussay_battle_tags.csv` file and comminicates with the COC api to retrieve the war information for each battletag. The data for each season is stored in the `Seasons Data` directory. 
- `Seasons Data`: Contains files `Pussay_season_data_{season}.csv` for each season. Each file contains the attack and defense data for each player and each battleday in the clan war league season.
- `keys.json`: storage of API keys


*Next Steps:*
- Create a script to read the data from the `Seasons Data` directory and create a summary and progress of the data for each player.