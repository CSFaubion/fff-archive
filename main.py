import json

# from espn_api.football import League

from patch.myleague import MyLeague as League

# this file is intended to be the entry point for this project. change the
# target year and enter your credentials into credentials.json

target_year = 2020

if __name__ == "__main__":
    # read credentials from file.
    creds = {}
    with open("credentials.json", "r") as credentials:
        creds = json.load(credentials)

    #create league object
    league = League(
        league_id=creds.get("leagueId", -1),
        year=target_year,
        espn_s2=creds.get("s2", None),
        swid=creds.get("swid", None)
    )

    print(league)