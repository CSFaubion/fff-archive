from espn_api.football import League

import time

from patch.playergame import PlayerGame


class ForeignKeyConstraint(Exception):
    pass


class MyLeague(League):
    def __init__(self, league_id: int, year: int, espn_s2=None, swid=None, username=None, password=None, debug=False):
        super().__init__(league_id=league_id, year=year, espn_s2=espn_s2,
                         swid=swid, username=username, password=password, debug=debug)
        self.get_owner_data()
        self.get_weekly_rosters()

    def get_owner_data(self):
        '''This function adds primaryOwner IDs to teams, and adds a
        list of league members that link to those IDs. there can be 
        more than one member per team'''
        espn_data = self.espn_request.league_get(params={'view': 'mTeam'})

        # add primary owner ids for teams
        team_data = espn_data.get('teams', None)
        if team_data is None:
            print('keyerror: failed to find key "teams"')
            exit(0)
        for team in self.teams:
            for espn_team in team_data:
                if espn_team['id'] == team.team_id:
                    team.primary_owner = espn_team.get('primaryOwner', '')

        # add member data
        member_data = espn_data.get('members', None)
        if member_data is None:
            print('keyerror: failed to find key "teams"')
            exit(0)
        for member in member_data:
            for team in self.teams:
                if team.primary_owner != member['id']:
                    continue
                else:
                    team.member = {
                        'display_name': member['displayName'],
                        'first_name': member['firstName'],
                        'espn_owner_id': member['id'],
                        'last_name': member['lastName']
                    }

    def _scoreboard_request(self, week):
        params = {
            'view': 'mScoreboard',
            'scoringPeriodId': week
        }
        return self.espn_request.league_get(params=params)

    def _get_all_rosters_in_schedule(self):
        '''Helper fucntion that returns a list of all games played in
        the season and the rosters for those games.'''
        # Get all games in schedule
        schedule = []
        roster_key = 'rosterForMatchupPeriod' if self.year <= 2017 else 'rosterForCurrentScoringPeriod'
        if self.current_week > self.settings.reg_season_count + 4:
            print("Error: Game count seems too high.")
        for i in range(1, (self.current_week+1)):
            # if year before 2018 skip week 15 and 17
            if self.year <= 2017:
                if (i == 15) or (i == 17):
                    continue
            time.sleep(5)
            data = self._scoreboard_request(week=i)
            # pull games with rosters out of week
            for game in data['schedule']:
                if roster_key in game['away'].keys():
                    # verify no missing game ids
                    if game.get('id', None) == None:
                        print('ERROR:PARSING ERROR NO GID')
                        exit(0)
                    schedule.append(game)
        return schedule

    def get_weekly_rosters(self):
        '''Gets all of the weekly rosters for the season.
        ESPN changes the format when they archive older seasons.
        For years 2017 and previous this function gets all starting 
        rosters for matchups, but no bench players.
        For years 2018 and later seasons this function gets all players on 
        rosters and their positions for each scoring period'''
        schedule = self._get_all_rosters_in_schedule()
        if self.year <= 2017:
            roster_key = 'rosterForMatchupPeriod'
        else:
            roster_key = 'rosterForCurrentScoringPeriod'
        weekly_rosters = {}
        for team in self.teams:
            weekly_rosters[team.team_id] = {}
            week = 1
            for game in schedule:
                if game['away']['teamId'] == team.team_id:
                    side = 'away'
                elif game['home']['teamId'] == team.team_id:
                    side = 'home'
                else:
                    continue
                weekly_rosters[team.team_id][week] = []
                game_id = game['id']
                for player in game[side][roster_key]['entries']:
                    weekly_rosters[team.team_id][week].append(
                        PlayerGame(player, self.year, week, game_id))
                week += 1
            endweek = (self.currentMatchupPeriod +
                       1) if self.year <= 2017 else (self.current_week + 1)
            if week != endweek:
                print('ERROR:NOT ENOUGH GAMES FOUND FOR TEAM', team.team_id)
                exit(0)

        for tid, roster in weekly_rosters.items():
            for team in self.teams:
                if tid != team.team_id:
                    continue
                else:
                    team.weekly_rosters = {}
                    for week, players in roster.items():
                        team.weekly_rosters[week] = players

    def check_foreign_key_constraints(self, data: dict):
        owner_ids = [x["espn_owner_id"] for x in data["owners"]]
        player_ids = [x["espn_id"] for x in data["players"]]
        team_ids = [x["espn_team_id"] for x in data["teams"]]
        roster_ids = [x["id"] for x in data["rosters"]]

        for team in data["teams"]:
            if team["owner_id"] not in owner_ids:
                raise ForeignKeyConstraint("Team:Owner")
        for draftpick in data["draftpicks"]:
            if draftpick["player_id"] not in player_ids:
                raise ForeignKeyConstraint("Draftpick:Player")
            if draftpick["team_id"] not in team_ids:
                raise ForeignKeyConstraint("Team:Draftpick")
        for roster in data["rosters"]:
            if roster["team_id"] not in team_ids:
                raise ForeignKeyConstraint("Team:Roster")
        for stat in data["stats"]:
            if stat["roster_id"] not in roster_ids:
                raise ForeignKeyConstraint("Roster:Stat")
            if stat["player_id"] not in player_ids:
                raise ForeignKeyConstraint("Stat:Player")

    def dump_league_data(self, integrity=False):
        '''this function outputs a dict that represents the league in
        the format I wanted to use for the database.'''
        # season
        season = {
            'league_id': self.league_id,
            'year': self.year,
            'league_name': self.settings.name
        }
        # teams
        teams = []
        for team in self.teams:
            temp = {
                # 'team_id' : AUTO
                # 'season_id' : AUTO
                'owner_id': team.primary_owner,
                'espn_team_id': team.team_id,
                'team_name': team.team_name,
                'abbrev': team.team_abbrev
            }
            teams.append(temp)
        # settings
        settings = {
            # 'setting_id' : AUTO
            # 'season_id' : AUTO
            'reg_season_count': self.settings.reg_season_count,
            'veto_votes_required': self.settings.veto_votes_required,
            'team_count': self.settings.team_count,
            'playoff_team_count': self.settings.playoff_team_count,
            'keeper_count': self.settings.keeper_count,
            # 'trade_deadline' : self.settings.trade_deadline,
            'tie_rule': self.settings.tie_rule,
            'playoff_seed_tie_rule': self.settings.playoff_seed_tie_rule
        }
        # owners
        owners = []
        for team in self.teams:
            owners.append(team.member)
        # players
        players = []
        p_map = {}
        for k, v in self.player_map.items():
            try:
                int(k)
            except ValueError:
                p_map[k] = v
        for k, v in p_map.items():
            players.append(
                {
                    'espn_player_name': k,
                    'position': None,
                    'espn_id': v
                }
            )
        # player lookup table to make sure we get all the players
        player_lookup = {}
        for player in players:
            player_lookup[player["espn_id"]] = player
        # draftpicks
        draftpicks = []
        for pick in self.draft:
            if player_lookup.get(pick.playerId, None) == None:
                temp = {
                    'espn_player_name': pick.playerName,
                    'position': None,
                    'espn_id': pick.playerId
                }
                player_lookup[pick.playerId] = temp
                players.append(temp)
            temp = {
                # 'draftpick_id ' : AUTO
                'team_id': pick.team.team_id,
                'player_id': pick.playerId,
                'round_num': pick.round_num,
                'round_pick': pick.round_pick,
                'pick_number': (((pick.round_num - 1) * self.settings.team_count) + pick.round_pick),
                'bid_amount': pick.bid_amount,
                'keeper_status': pick.keeper_status
            }
            draftpicks.append(temp)
        # rosters and stats
        rosters = []
        stats = []
        rid = 0
        for team in self.teams:
            for week, game in team.weekly_rosters.items():
                tot_points = 0
                proj_points = 0
                for player in game:
                    if player_lookup.get(player.playerId, None) == None:
                        temp = {
                            'espn_player_name': player.name,
                            'position': None,
                            'espn_id': player.playerId
                        }
                        player_lookup[player.playerId] = temp
                        players.append(temp)
                    tot_points += player.total_points
                    proj_points += player.projected_total_points
                    gid = player.game_id
                    temp_stat = {
                        # 'stat_id' : AUTO
                        'player_id': player.playerId,
                        'roster_id': rid,
                        'total_points': player.total_points,
                        'projected_points': player.projected_total_points,
                        'starting': True if player.lineup_slot != 'BE' else False,
                        'position': player.lineup_slot,
                        'pro_team': player.proTeam,
                        'scoring_period': week
                    }
                    stats.append(temp_stat)
                temp = {
                    'id': rid,
                    'team_id': team.team_id,
                    'game_id': gid,
                    'total_points': tot_points,
                    'projected_points': proj_points,
                    'scoring_period': week
                }
                rid += 1
                rosters.append(temp)
        output_data = {
            "season": season,
            "owners": owners,
            "players": players,
            "settings": settings,
            "teams": teams,
            "draftpicks": draftpicks,
            'rosters': rosters,
            'stats': stats
        }
        try:
            self.check_foreign_key_constraints(output_data)
        except ForeignKeyConstraint as e:
            if integrity == True:
                raise e
            else:
                return output_data
