from espn_api.football import League

import time

from playergame import PlayerGame


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
        if self.current_week > 17:
            print("Error: Current week greater than 17")
        for i in range(1, (self.current_week+1)):
            # if year before 2018 skip week 15 and 17
            if self.year <= 2017:
                if (i == 15) or (i == 17):
                    continue
            time.sleep(5)
            data = self._scoreboard_request(year=self.year, week=i)
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

        return weekly_rosters

    def to_json(self):
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
            'playoff_team_count ': self.settings.playoff_team_count,
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
        return {
            "season": season,
            "owners": owners,
            "players": players,
            "settings": settings,
            "teams": teams
        }
