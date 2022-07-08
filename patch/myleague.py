from espn_api.football import League

import time
# this patch is intended to add some data from espn that the espn-api
# package doesn't keep.


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

    def get_weekly_rosters(self):
        '''Gets all of the weekly rosters for the season.
        ESPN changes the format when they archive older seasons.
        For years 2017 and previous this function gets all starting 
        rosters for matchups, but no bench players.
        For years 2018 and later seasons this function gets all players on 
        rosters and thier positions for each scoring period'''
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
                    schedule.append(game)
         # verify no missing game ids
        for game in schedule:
            gid = game.get('id', None)
            if gid == None:
                print('ERROR:PARSING ERROR NO GID')
                exit(0)
