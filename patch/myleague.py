from espn_api.football import League

class MyLeague(League):
    def __init__(self, league_id: int, year: int, espn_s2=None, swid=None, username=None, password=None, debug=False):
        super().__init__(league_id=league_id, year=year, espn_s2=espn_s2, swid=swid, username=username, password=password, debug=debug)

        #TODO: add primary owner ids for teams
        espn_data = self.espn_request.league_get(params={'view': 'mTeam'})
        teamdata = espn_data.get('teams', None)
        

        #TODO: get weekly rosters
