import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from patch.myleague import MyLeague as League
from db.db import add_league, Base

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


    with open("league"+str(target_year)+".json", "w") as outfile:
        data = json.dump(league.dump_league_data(), outfile, indent=2)

    with open("league"+str(target_year)+".json", "r") as infile:
        engine = create_engine("sqlite+pysqlite:///b.db", echo=False, future=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        add_league(session, data)
    
