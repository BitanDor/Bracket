from enum import Enum

PLAYOFF_1 = "playoff single game"  # e.g., UCL final, WC playoff
PLAYOFF_2 = "playoff two games home and away"  # e.g., UCL - R1, QF, and SF
PLAYOFF_3 = "playoff series best out of three"
PLAYOFF_5 = "playoff series best out of five"
PLAYOFF_7 = "playoff series best out of seven"  # e.g., NBA Playoff R1, QF, SF, Final
NBA_PLAY_IN = "NBA play-in"  # specific feeds
GROUPS = "groups"  # e.g., UCL group stage or WC group stage
TOURNAMENT_POSSIBLE_STAGES = [PLAYOFF_1, PLAYOFF_2, NBA_PLAY_IN, GROUPS]





class ResultType(Enum):
    # types we have:
    # a single game with only winner or loser
    # a playoff series

    PLAYOFF_GAME =  {"winner": "either team a or team b"}
    PLAYOFF_SERIES_3 = {"winner": "team a or team b",
                           "games": 3}    # integer - 2 or 3
    PLAYOFF_SERIES_5 = {"winner": "team a or team b",
                           "games": 5}    # integer - 3, 4, or 5
    PLAYOFF_SERIES_7 = {"winner": "team a or team b",
                           "games": 7}    # integer - 4, 5, 6, or 7
    SOCCER_WINNER_LOSER_DRAW =
    SOCCER_HOME_AND_AWAY =

class Match:
    def __init__(self, team_a="team a", team_b= "team b", match_type=None, result = None, stage = None, index = None, tournament_id = None):
        self.team_a = team_a
        self.team_b = team_b