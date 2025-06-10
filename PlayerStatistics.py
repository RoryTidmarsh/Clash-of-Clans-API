"""The statistics creations for each member of the clan 'Pussay Palace'.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

class PlayerStatistics:
    def __init__(self, first_season=None, last_season=None):

        filepath = os.path.join(os.path.dirname(__file__), "Seasons Data", "Pussay_season_database.csv")
        self.all_attack_data = pd.read_csv(filepath)
        self.player_names = self.all_attack_data["name"].unique()
        self.player_names = [name for name in self.player_names if name != "Pussay Palace"]
        self.first_season = first_season
        self.last_season = last_season
        # print(f"Total unique players: {self.player_names}")

    def get_player_data(self, player_name):
        """Retrieve the data for a given player from the 'Pussay Palace' clan."""
        player_data = self.all_attack_data[self.all_attack_data["name"] == player_name]
        if self.first_season:
            player_data = player_data[player_data["season"] >= self.first_season]
        if self.last_season:
            player_data = player_data[player_data["season"] <= self.last_season]
        return player_data.reset_index(drop=True)

    def get_player_statistics(self, player_name):
        """Retrieve the statistics for a given player from the 'Pussay Palace' clan."""
        player_data = self.get_player_data(player_name)
        stats = player_data.groupby(['name', 'season']).mean(numeric_only=True).reset_index()
        stats["missed_attacks"] = player_data.groupby(['name', 'season'])["attackStars"].apply(lambda x: x.isna().sum()).values
        return stats
    
    def all_players_statistics(self):
        """Retrieve the statistics for all players from the 'Pussay Palace' clan."""
        all_stats = []
        for player in self.player_names:
            stats = self.get_player_statistics(player)
            all_stats.append(stats)
        return pd.concat(all_stats).reset_index(drop=True)

# Example usage
stats = PlayerStatistics()
print(stats.all_players_statistics())

# Example usage
# print(get_player_statistics(player_names[3]))