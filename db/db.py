import json
from typing import List

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from base import Base
from draftpick_dto import Draftpick
from owner_dto import Owner
from player_dto import Player
from roster_dto import Roster
from season_dto import Season
from setting_dto import Setting
from stat_dto import Stat
from team_dto import Team

# engine = sqlalchemy.create_engine(
#     "sqlite+pysqlite:///:memory:", echo=True, future=True)
engine = sqlalchemy.create_engine("sqlite+pysqlite:///b.db", echo=False, future=True)


def check_relationships(
    season: Season,
    setting: Setting,
    teams: List[Team],
    draftpicks: List[Draftpick],
    rosters: List[Roster],
    stats: List[Stat],
):
    assert season.setting is not None
    assert setting.season is not None
    for team in teams:
        assert team.primary_owner is not None
        assert team.season is not None
        assert len(team.draftpicks) > 0
        assert len(team.rosters) > 0
    for pick in draftpicks:
        assert pick.team is not None
        assert pick.player is not None
    for roster in rosters:
        assert roster.team is not None
        assert len(roster.stats) > 0
    for stat in stats:
        assert stat.roster is not None
        assert stat.player is not None
    assert len(teams) == setting.team_count
    # assert(len(rosters) == setting.team_count * (setting.reg_season_count + 4))


def insert_unknown_players(
    session: sqlalchemy.orm.session.Session, player_lookup: dict
):
    players = session.query(Player).all()
    players_by_id = {player.espn_id: player for player in players}
    for id, player in player_lookup.items():
        if id not in players_by_id:
            session.add(player)

    session.commit()


def insert_unknown_owners(session: sqlalchemy.orm.session.Session, owner_lookup: dict):
    owners = session.query(Owner).all()
    owners_by_id = {owner.espn_owner_id: owner for owner in owners}
    for id, owner in owner_lookup.items():
        if id not in owners_by_id:
            session.add(owner)

    session.commit()


def season_exists(session: sqlalchemy.orm.session.Session, season: Season):
    return (
        session.query(Season)
        .filter(Season.league_id == season.league_id, Season.year == season.year)
        .one_or_none()
    )


def add_league(session: sqlalchemy.orm.session.Session, data: dict):
    # # add data
    season = Season(**data["season"])
    setting = Setting(**data["settings"])
    players = [Player(**player) for player in data["players"]]
    owners = [Owner(**owner) for owner in data["owners"]]
    teams = [Team(**team) for team in data["teams"]]
    draftpicks = [Draftpick(**pick) for pick in data["draftpicks"]]
    rosters = [Roster(**roster) for roster in data["rosters"]]
    stats = [Stat(**stat) for stat in data["stats"]]

    assert season_exists(session=session, season=season) is None

    insert_unknown_players(session, {player.espn_id: player for player in players})
    player_lookup = {player.espn_id: player for player in session.query(Player).all()}

    insert_unknown_owners(session, {owner.espn_owner_id: owner for owner in owners})
    owners = [owner for owner in session.query(Owner).all()]

    # # add relationships
    # seasons:settings
    setting.season = season

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

    for pick in draftpicks:
        espn_player_id = pick.player_id
        pick.player_id = None
        temp = player_lookup.get(espn_player_id, None)
        assert temp is not None
        # draftpicks:players
        pick.player = temp
        espn_team_id = pick.team_id
        pick.team_id = None
        for team in teams:
            if team.espn_team_id == espn_team_id:
                # draftpicks:teams
                pick.team = team
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
        assert temp is not None
        # stats:players
        stat.player = temp
        roster_id = stat.roster_id
        stat.roster_id = None
        for roster in rosters:
            if roster_id == roster.id:
                # stats:rosters
                stat.roster = roster
                break

    # reset roster id to None after tying stat to roster
    for roster in rosters:
        roster.id = None

    check_relationships(
        season=season,
        setting=setting,
        teams=teams,
        draftpicks=draftpicks,
        rosters=rosters,
        stats=stats,
    )

    session.add(season)
    session.add(setting)
    session.add_all(teams)
    session.add_all(draftpicks)
    session.add_all(rosters)
    session.add_all(stats)

    session.commit()


if __name__ == "__main__":
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    for i in range(2014, 2022):
        with open("league" + str(i) + ".json", "r") as infile:
            data = json.load(infile)

        add_league(session, data)
