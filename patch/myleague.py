from espn_api.football import League

# this patch is intended to add some data from espn that the espn-api 
# package doesn't keep.


class MyLeague(League):
    def __init__(self, league_id: int, year: int, espn_s2=None, swid=None, username=None, password=None, debug=False):
        super().__init__(league_id=league_id, year=year, espn_s2=espn_s2,
                         swid=swid, username=username, password=password, debug=debug)

        # TODO: add primary owner ids for teams
        espn_data = self.espn_request.league_get(params={'view': 'mTeam'})
        teamdata = espn_data.get('teams', None)
        if teamdata is None:
            print('keyerror: failed to find key "teams"')
            exit(0)
        # for each team, add the corresponding espn owner id from the espn data.
        for team in self.teams:
            for espn_team in teamdata:
                if espn_team['id'] == team.team_id:
                    team.primary_owner = espn_team.get('primaryOwner', '')

        # TODO: add member data

        # TODO: get weekly rosters
