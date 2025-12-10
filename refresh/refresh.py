from refresh.Find_battletags import load_battle_tags_supabase
from refresh.COC_client import clan_data
from refresh.reading_WarData import load_warData_supabase

if __name__ == "__main__":
    clan_tag = clan_data["clan_tag"]
    clan_name = clan_data["clan_name"]
    base_url = clan_data["base_url"]
    url = clan_data["url"]
    headers = clan_data["headers"]

    # Find and Load battle tags into Supabase
    load_battle_tags_supabase(clan_tag)

    # read individual war data
    load_warData_supabase()

