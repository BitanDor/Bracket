from enum import Enum
from datetime import datetime
from typing import Tuple, Dict, List, Optional, Union
from pydantic import BaseModel, Field
# TODO: use Field to specify rules regarding data

from typing import TypeAlias
import uuid6 # we use uuid6.uuid7()

userId: TypeAlias = uuid6.UUID
stageId: TypeAlias = uuid6.UUID
matchID: TypeAlias = uuid6.UUID
tournamentId: TypeAlias = uuid6.UUID
teamId: TypeAlias = uuid6.UUID
privateBracketId = uuid6.UUID

singleMatchScore = Tuple[int, int]

UserBracketGuess = Dict[matchID, Union[FinalScore, DetailedScore]]

NINTY_MINUTES = "ninty_minutes"
FIRST_MATCH_NINTY_MINUTES = "first_match_ninty_minutes"
RETURN_LEG_NINTY_MINUTES = "return_leg_ninty_minutes"
OVER_TIME = "over_time"
PENALTIES = "penalties"

class StageType(Enum):
    GROUP_STAGE = "group stage" # to be presented in the UI as a table with scores
    PLAYOFF_STAGE = "playoff stage" # to be presented in the UI as a playoff tree
    PLAY_IN_STAGE = "play-in stage" # to be presented in the UI as a separate playoff tree, possibly with a special
    # structure like the NBA Play In stage, or UCL primary stage (before the group stage starts)

class FinalScore(Enum):
    HOME_WIN = "home win"
    DRAW = "draw"
    AWAY_WIN = "away win"

class PossibleFinalScore(Enum):
    WINNER_LOSER = "win, lose" # note that the loser may also advance!
    WIN_DRAW_LOSS = "win, draw, lose"

class DetailedScore(Enum):
    SOCCER_SINGLE_NON_DECISIVE_MATCH = singleMatchScore
    SOCCER_SINGLE_DECISIVE_MATCH = {
        NINTY_MINUTES: singleMatchScore,
        OVER_TIME: singleMatchScore,
        PENALTIES: singleMatchScore
    }
    SOCCER_HOME_AND_AWAY_DECISIVE_MATCH = {
        FIRST_MATCH_NINTY_MINUTES: singleMatchScore,
        RETURN_LEG_NINTY_MINUTES: singleMatchScore,
        OVER_TIME: singleMatchScore,
        PENALTIES: singleMatchScore
    }
    BASKETBALL_SERIES = singleMatchScore

class UserRole(Enum):
    REGULAR = "regular"
    ADMIN = "admin"


class Team(BaseModel):
    team_id: teamId
    team_name: str
    team_emoji: str
    team_national_flag: str
    team_image_file_location: str
    def store_to_database(self):
        # TODO: implement this method to store the team information in the database
        pass
    def update(
            self,
            team_name: Optional[str] = None,
            team_emoji: Optional[str] = None,
            team_national_flag: Optional[str] = None,
            team_image_file_location: Optional[str] = None):
        if team_name is not None:
            self.team_name = team_name
        if team_emoji is not None:
            self.team_emoji = team_emoji
        if team_national_flag is not None:
            self.team_national_flag = team_national_flag
        if team_image_file_location is not None:
            self.team_image_file_location = team_image_file_location


class Stage(BaseModel):
    stage_id: stageId
    stage_name: str
    stage_type: StageType
    stage_possible_final_score: PossibleFinalScore
    stage_possible_detailed_score: DetailedScore


class User(BaseModel):
    user_id: userId
    user_unique_username: str # must be unique
    user_first_name: str
    user_last_name: str
    user_email: str
    user_hashed_password: str
    user_role: UserRole
    user_active_tournaments: Dict[tournamentId, UserBracketGuess]
    user_past_tournaments: Dict[tournamentId, UserBracketGuess]
    def store_to_database(self):
        # TODO: implement this method to store the team information in the database
        pass
    def update(
            self,
            user_first_name: Optional[str] = None,
            user_last_name: Optional[str] = None,
            user_email: Optional[str] = None,
            user_hashed_password: Optional[str] = None,
            user_role: Optional[UserRole] = None):
        if user_first_name is not None:
            self.user_first_name = user_first_name
        if user_last_name is not None:
            self.user_last_name = user_last_name
        if user_email is not None:
            self.user_email = user_email
        if user_hashed_password is not None:
            self.user_hashed_password = user_hashed_password
        if user_role is not None:
            self.user_role = user_role


class TournamentPrivateBracket(BaseModel):
    tournament_private_bracket_id: privateBracketId
    tournament_private_bracket_tournament: tournamentId
    tournament_private_bracket_join_link: str
    tournament_private_bracket_participants_users_ids: List[userId]
    tournament_private_bracket_manager_user_id: userId
    tournament_private_bracket_whatsapp_group_connection_details: str
    tournament_private_bracket_leaderboard = Dict[userId , int]  # TODO: also store the guessed tournament winner


class Match(BaseModel):
    match_id: matchID
    match_home_team: teamId
    match_away_team: teamId
    match_scheduled_time: datetime
    match_final_score: PossibleFinalScore
    match_detailed_score: DetailedScore


class Tournament(BaseModel):
    tournament_id: tournamentId
    tournament_name: str
    tournament_participating_teams: List[teamId]
    tournament_stages: List[stageId]
    tournament_matches: list[Match]  # This is the main object here. It contains all the matches. First with "TBD".
    tournament_participating_users: set[userId]
    tournament_private_brackets: list[privateBracketId]
    def store_to_database(self):
        pass
    def update_true_results_and_process(self, true_results: Dict[matchID, Union[FinalScore, DetailedScore]]):
        pass

