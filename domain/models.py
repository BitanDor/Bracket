from enum import Enum
from datetime import datetime
from typing import TypeAlias, Tuple, Dict, List, Optional, Union, Set
import uuid # we use uuid6.uuid7() to generate ids, but uuid to read them from str
from pydantic import BaseModel, Field, EmailStr, ConfigDict
# TODO: use Field to specify rules regarding data validation, e.g., for email format, password strength, etc.

userId: TypeAlias = uuid.UUID
stageId: TypeAlias = uuid.UUID
matchId: TypeAlias = uuid.UUID
teamId: TypeAlias = uuid.UUID
tournamentId: TypeAlias = uuid.UUID
privateBracketId: TypeAlias = uuid.UUID
groupId: TypeAlias = uuid.UUID
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

class SourceType(str, Enum):
    MATCH = "match"
    GROUP = "group"

class SelectionRule(str, Enum):
    WINNER = "winner"
    LOSER = "loser"
    RANK_1 = "rank_1"
    RANK_2 = "rank_2"
    RANK_3 = "rank_3"
    LAMBDA = "lambda" # for more complex selection rules that don't fit the above categories,
    # e.g., "best 4th place teams across all groups" - in this case, the actual logic will be implemented
    # in the Tournament.update_true_results_and_process() method, and the rule will be identified by a unique
    # string key that is used to trigger the correct logic branch.

# --- Updated Wiring Models ---
class DependencySource(BaseModel):
    """Defines where a team in a match slot comes from (Match or Stage Table)"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    source_id: Union[matchId, groupId]
    source_type: SourceType
    rule: SelectionRule

class DependencyTarget(BaseModel):
    """Output: Where do I send my results?"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    target_id: Union[matchId, groupId]
    # 'home', 'away' for matches, or 'group_member' for groups
    target_slot: str
    rule: SelectionRule

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

class TeamStats(BaseModel):
    games_played: int = 0
    won: int = 0
    draw: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0

class Stage(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    stage_id: stageId
    stage_name: str
    stage_type: StageType
    stage_possible_detailed_score: DetailedScoreType


class Group(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    group_id: groupId
    stage_id: stageId
    group_name: str
    participating_teams: List[teamId] = []
    team_stats: Dict[teamId, TeamStats] = {}
    member_matches: List[matchId] = [] # The matches that feed this group's stats
    input_sources: List[DependencySource] = [] # Who feeds this group's team list
    output_targets: List[DependencyTarget] = [] # Where do my ranked teams go
    has_ended: bool = False

class Match(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    match_id: matchId
    home_team_id: Optional[teamId] = None
    away_team_id: Optional[teamId] = None
    match_guess_time_windows: Dict[stageId, Tuple[datetime, datetime]] = Field(default_factory=dict) # determines how many points a guess is worth based on WHEN it was made.
    stage_id: stageId
    home_source: Optional[DependencySource] = None
    away_source: Optional[DependencySource] = None
    output_targets: List[DependencyTarget] = []
    score: MatchScore = MatchScore.PENDING
    detailed_score: Optional[DetailedScore] = None
    scheduled_time: Optional[str] = None
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


class ScoringConfig(BaseModel):
    """Configuration for the scoring engine"""
    # Map: TournamentStageName -> { GuessTimeStageName: BasePoints }
    # Example: "FINALS": {"BASE": 8, "R1": 4}
    points_map: Dict[str, Dict[str, float]]
    detailed_score_multiplier: float = 2.0 # Multiplier for points when detailed score is guessed correctly


class Tournament(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    tournament_id: tournamentId
    tournament_name: str
    participating_teams: List[teamId]
    stages: List[Stage]
    groups: List[Group] = []
    matches: List[Match]
    participating_users: Set[userId]
    private_brackets: list[privateBracketId]
    scoring_config: ScoringConfig

