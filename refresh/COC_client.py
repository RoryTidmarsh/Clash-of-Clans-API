"""Clash of Clans API client module.
WIP, currently COC API calls are made directly in refresh scripts.

API calls for accesing the CWL tags are different to actually accessing the clan data,
so future steps are to have seperate functions in here that the refresh scripts can call.
"""

from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '.env.refresh'))
coc_api_key = os.getenv("COC_API_KEY") # COC API key (loaded from .env.refresh)

# Response codes from the API
response_codes = {
    200: "Success",
    400: "Client provided incorrect parameters for the request.",
    403: "Access denied, either because of missing/incorrect credentials or used API token does not grant access to the requested resource. Check the Api Key.",
    404: "The requested resource does not exist.",
    429: "Too many requests. You are rate limited. Wait before sending more requests.",
    500: "Server error. Something is wrong on Clash of Clans side.",
    503: "Server is down for maintenance.",
}


# Pussay Clan Tag
clan_tag = "%23CQGY2LQU"
clan_name = "Pussay Palace"
base_url = "https://api.clashofclans.com/v1"
url = base_url + f"/clans/{clan_tag}"
headers = {
    "Accept": "application/json",
    "authorization": "Bearer %s" % coc_api_key,
}

clan_data = {
    "clan_tag": clan_tag,
    "clan_name": clan_name,
    "base_url": base_url,
    "url": url,
    "headers": headers,
}


if __name__ == "__main__":
    print("COC_client module loaded.")
    