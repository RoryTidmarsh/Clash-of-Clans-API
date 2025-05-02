import pandas as pd
import numpy as np
import requests

# Dictionary containing the API key, add your own key for your IP address
# You can get your own key from https://developer.clashofclans.com
keys = {"rory": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImZmNThkODRjLTVmYWItNDc3Ny1iY2M0LTA5OTc3ZGRjYWM4ZSIsImlhdCI6MTczODU4NzUyOSwic3ViIjoiZGV2ZWxvcGVyLzM3MjExZmI5LTgzODMtNDA1OS05MDFlLTFlNmFmZDBmYzFkNCIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjgyLjQ3LjMzLjE2MyJdLCJ0eXBlIjoiY2xpZW50In1dfQ.QOKe0Vjh2nVam7H8KM3feYh0c8sPQcR_gLRDhUWjCBYjKUgFBxTrgOaWb3BvzKx-X3Ae0OrrcEk6II7y_JmZGw"}

# Pussay Clan Tag
clan_tag = "%23CQGY2LQU"
url = f"https://api.clashofclans.com/v1/clans/{clan_tag}"
headers = {
    "Accept": "application/json",
    "authorization": "Bearer %s" % keys["rory"],
}

# Make the request to the API
response = requests.request("GET", url, headers=headers)
data = response.json()

# Find rozzledog72 in the member list and print their tag and role
for member in data["memberList"]:
    if member["name"] == "rozzledog 72":
        print("Name:", member["name"])
        print("Role:", member["role"])
        print("Trophies:", member["trophies"])
        print("TH level:",member["townHallLevel"])