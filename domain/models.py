from enum import Enum
from datetime import datetime
from typing import TypeAlias, Tuple, Dict, List, Optional, Union
import uuid6 # we use uuid6.uuid7()
from pydantic import BaseModel, Field, EmailStr, ConfigDict
# TODO: use Field to specify rules regarding data validation, e.g., for email format, password strength, etc.

userId: TypeAlias = uuid6.UUID
stageId: TypeAlias = uuid6.UUID
matchId: TypeAlias = uuid6.UUID
teamId: TypeAlias = uuid6.UUID
tournamentId: TypeAlias = uuid6.UUID
privateBracketId: TypeAlias = uuid6.UUID

SingleMatchScore: TypeAlias = Tuple[int, int]

class StageType(str, Enum):
    GROUP_STAGE = "group stage"  # to be presented in the UI as a table with scores
    PLAYOFF_STAGE = "playoff stage"  # to be presented in the UI as a playoff tree
    PLAY_IN_STAGE = "play-in stage"  # to be presented in the UI as a separate playoff tree, possibly with a special
    # structure like the NBA Play In stage, or UCL primary stage (before the group stage starts)

class MatchScore(str, Enum):
    HOME_WIN = "1"  # home team can play away - e.g., in the return leg, or in certain games in an NBA series
    DRAW = "X"
    AWAY_WIN = "2"
    PENDING = "TBD"

class UserRole(str, Enum):
    REGULAR = "regular"
    ADMIN = "admin"

class NonDecisiveMatchScore(BaseModel):
    regular_time: SingleMatchScore
    is_final: bool = False

class DecisiveMatchScore(BaseModel):
    regular_time: SingleMatchScore
    extra_time: Optional[SingleMatchScore] = None
    penalties_shootout: Optional[SingleMatchScore] = None
    is_final: bool = False

class HomeAndAwayScore(BaseModel):
    leg1: SingleMatchScore
    leg2: SingleMatchScore
    extra_time: Optional[SingleMatchScore] = None
    penalties_shootout: Optional[SingleMatchScore] = None
    is_final: bool = False

class BasketballSeriesScore(BaseModel):
    home_wins: int
    away_wins: int
    is_final: bool = False

DetailedScore = Union[NonDecisiveMatchScore, DecisiveMatchScore, HomeAndAwayScore, BasketballSeriesScore]

class DetailedScoreType(str, Enum):
    NON_DECISIVE = "non_decisive"
    DECISIVE = "decisive"
    HOME_AWAY = "home_away"
    SERIES = "series"

class MatchGuessData(BaseModel):
    score: MatchScore
    detailed_score: Optional[DetailedScore] = None
    when_edited: datetime = Field(default_factory=datetime.now)

UserBracketGuess: TypeAlias = Dict[matchId, MatchGuessData]

class Team(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    team_id: teamId
    team_name: str
    team_emoji: str
    team_national_flag: str
    team_image_file_location: str
    def store_to_database(self):
        # TODO: Implement database persistence logic for Teams
        pass
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)

class Stage(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    stage_id: stageId
    stage_name: str
    stage_type: StageType
    stage_possible_detailed_score: DetailedScoreType


class Match(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    match_id: matchId
    home_team_id: Optional[teamId] = None
    away_team_id: Optional[teamId] = None
    scheduled_time: datetime
    stage_id: stageId
    score: MatchScore = MatchScore.PENDING
    detailed_score: Optional[DetailedScore] = None
    has_ended: bool = False

class PrivateBracket(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    bracket_id: privateBracketId
    tournament_id: tournamentId
    join_link: str
    participants_ids: List[userId]
    manager_id: userId
    leaderboard: Dict[userId, int] = {}  # TODO: also store the guessed tournament winner
    whatsapp_group_connection_details: Optional[str] = None # TODO: Implement WhatsApp integration for automated updates


class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    user_id: userId
    username: str # Must be unique
    first_name: str
    last_name: str
    email: EmailStr
    hashed_password: str
    role: UserRole = UserRole.REGULAR
    active_tournaments: Dict[tournamentId, UserBracketGuess] = {}
    past_tournaments: Dict[tournamentId, UserBracketGuess] = {}
    def store_to_database(self):
        # TODO: Implement database persistence logic for Users
        pass
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)


class Tournament(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    tournament_id: tournamentId
    tournament_name: str
    participating_teams: List[teamId]
    stages: List[Stage]
    matches: list[Match]
    participating_users: set[userId]
    private_brackets: list[privateBracketId]
    def store_to_database(self):
        # TODO: Implement tournament serialization to Supabase
        pass
    def update_true_results_and_process(self, results: Dict[matchId, MatchGuessData]):
        """
        Main engine function:
        1. Updates actual match scores.
        2. Triggers re-calculation for all participating users' scores.
        3. Updates leaderboards for all linked PrivateBrackets.
        4. Processes "Feed Forward" logic for subsequent matches (TBD -> Team).
        """
        # TODO: Implement the scoring and propagation engine logic
        pass

