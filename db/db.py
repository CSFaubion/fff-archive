import json

import sqlalchemy
from sqlalchemy.orm import registry, sessionmaker

from base import Base
from draftpick_dto import Draftpick
from owner_dto import Owner
from player_dto import Player
from roster_dto import Roster
from season_dto import Season
from setting_dto import Setting
from stat_dto import Stat
from team_dto import Team

engine = sqlalchemy.create_engine(
    "sqlite+pysqlite:///:memory:", echo=True, future=True)
# engine = sqlalchemy.create_engine(
#     "sqlite+pysqlite:///b.db", echo=True, future=True)


def add_league(session, data):
    # # add data
    season = Season(**data["season"])
    setting = Setting(**data["settings"])
    players = [Player(**player) for player in data["players"]]
    owners = [Owner(**owner) for owner in data["owners"]]
    teams = [Team(**team) for team in data["teams"]]
    draftpicks = [Draftpick(**dp) for dp in data["draftpicks"]]
    rosters = [Roster(**roster) for roster in data["rosters"]]
    stats = [Stat(**stat) for stat in data["stats"]]

    # # add relationships
    # seasons:settings
    setting.season = season

    player_lookup = {}
    for player in players:
        player_lookup[player.espn_id] = player

    for team in teams:
        # seasons:teams
        team.season = season

        # teams:owners
        owner_id = team.owner_id
        team.owner_id = None
        for owner in owners:
            if owner_id == owner.espn_owner_id:
                team.primary_owner = owner
                break

    for dp in draftpicks:
        espn_player_id = dp.player_id
        dp.player_id = None
        temp = player_lookup.get(espn_player_id, None)
        assert(temp is not None)
        # draftpicks:players
        dp.player = temp
        espn_team_id = dp.team_id
        dp.team_id = None
        for team in teams:
            if team.espn_team_id == espn_team_id:
                # draftpicks:teams
                dp.team = team
                break

    for roster in rosters:
        # teams:rosters
        espn_team_id = roster.team_id
        roster.team_id = None
        for team in teams:
            if team.espn_team_id == espn_team_id:
                roster.team = team
                break

    for stat in stats:
        player_id = stat.player_id
        stat.player_id = None
        temp = player_lookup.get(player_id, None)
        assert(temp is not None)
        # stats:players
        stat.player = temp
        roster_id = stat.roster_id
        stat.roster_id = None
        for roster in rosters:
            if roster_id == roster.id:
                # stats:rosters
                stat.roster = roster
                break

    # reset roster id to None after tying roster to stat
    for roster in rosters:
        roster.id = None

    session.add(season)
    session.add(setting)
    session.add_all(players)
    session.add_all(owners)
    session.add_all(teams)
    session.add_all(draftpicks)
    session.add_all(rosters)
    session.add_all(stats)

    session.commit()


if __name__ == "__main__":
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    with open("league2014.json", "r") as infile:
        data = json.load(infile)

    add_league(session, data)
