from espn_api.football import League

# this patch is intended to add some data from espn that the espn-api
# package doesn't keep.


class MyLeague(League):
    def __init__(self, league_id: int, year: int, espn_s2=None, swid=None, username=None, password=None, debug=False):
        super().__init__(league_id=league_id, year=year, espn_s2=espn_s2,
                         swid=swid, username=username, password=password, debug=debug)
        self.get_owner_data()

        # TODO: get weekly rosters


    def get_owner_data(self):

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
                        'display_name' : member['displayName'],
                        'first_name' : member['firstName'],
                        'espn_owner_id' : member['id'],
                        'last_name' : member['lastName']
                    }
