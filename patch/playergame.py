from espn_api.football import Player
from espn_api.football.constant import POSITION_MAP


class PlayerGame(Player):
    """adds lineup slot, scoring period, and game_id to Player class.
    expects to be given player objects from scoreboard requests instead
    of roster requests. represents a player in a game."""

    def __init__(self, data, year, week, game_id):
        super().__init__(data=data, year=year)
        if self.total_points == 0:
            self.total_points = data["playerPoolEntry"]["appliedStatTotal"]
        if self.projected_total_points == 0:
            self.projected_total_points = self.stats.get(week, {}).get(
                "projected_points", 0
            )

        if year < 2018:
            self.lineup_slot = self.position
        else:
            lineup_slot_id = data["lineupSlotId"]
            self.lineup_slot = POSITION_MAP[lineup_slot_id]

        self.scoring_period = week
        self.season = year
        self.game_id = game_id
