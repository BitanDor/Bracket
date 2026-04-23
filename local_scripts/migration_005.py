import json
import uuid6
from datetime import datetime
from typing import Dict, List
from domain.models import (
    Tournament, Stage, Match, StageType, DetailedScoreType,
    MatchScore, tournamentId
)
import tournaments.nba_2026_config as nba_cfg
import tournaments.ucl_2026_config as ucl_cfg

# Fixed IDs from previous migration
NBA_TOURNAMENT_ID = uuid6.UUID("019dbbe0-fb87-7065-96f5-b4e509a4aa74")
UCL_TOURNAMENT_ID = uuid6.UUID("019dbbe0-fb86-771f-8c54-c3f07108f0b4")

def load_teams_map() -> Dict[str, str]:
    """Maps Team Name -> Team UUID string from teams.json"""
    with open("../Bracket/data/v2_local/teams.json", "r", encoding="utf-8") as f:
        teams_data = json.load(f)
    return {details["team_name"]: tid for tid, details in teams_data.items()}


def create_stages(stage_names: List[str], tournament_type: str) -> Dict[str, Stage]:
    """Creates Stage objects based on tournament context (NBA vs UCL)"""
    stages_map = {}
    for name in stage_names:
        s_id = uuid6.uuid7()

        # Logic to determine StageType and ScoreType based on name and tournament
        if tournament_type == "NBA":
            s_type = StageType.PLAY_IN_STAGE if "PLAY_IN" in name else StageType.PLAYOFF_STAGE
            score_type = DetailedScoreType.SERIES
        else:  # UCL
            s_type = StageType.PLAYOFF_STAGE  # UCL knockout is playoff-style tree
            score_type = DetailedScoreType.DECISIVE if name == "FINAL" else DetailedScoreType.HOME_AWAY

        stages_map[name] = Stage(
            stage_id=s_id,
            stage_name=name,
            stage_type=s_type,
            stage_possible_detailed_score=score_type
        )
    return stages_map


def migrate_tournament(config, t_id: tournamentId, t_type: str, teams_map: Dict[str, str]):
    print(f"📦 Migrating {config.NAME}")

    # 1. Create Stages
    stages_instances = create_stages(config.STAGES, t_type)

    # 2. Build Matches
    matches_list = []
    # Helper to map old match identifiers to new UUIDs for cross-referencing
    match_id_mapping = {}

    # We iterate over BRACKET_STRUCTURE to create all playoff matches
    # In NBA, we also need to account for initial teams in TEAMS dict
    all_match_keys = list(config.TEAMS.keys()) + list(config.BRACKET_STRUCTURE.keys())

    # Remove duplicates while preserving order
    all_match_keys = list(dict.fromkeys(all_match_keys))

    for m_key in all_match_keys:
        m_id = uuid6.uuid7()
        match_id_mapping[m_key] = m_id

        # Determine the Stage ID
        current_stage_name = "UNKNOWN"
        for s_name in config.STAGES:
            if m_key.startswith(s_name) or s_name in m_key:
                current_stage_name = s_name
                break

        stage_obj = stages_instances.get(current_stage_name)

        # Determine Participants (Home/Away)
        # Check if it's an initial match (from TEAMS) or a bracket match
        participants = config.TEAMS.get(m_key) or config.BRACKET_STRUCTURE.get(m_key)

        home_id, away_id = None, None
        if participants:
            p1, p2 = participants[0], participants[1]
            # If p1 is a team name in our map, use its ID. Otherwise, it's a TBD Match reference.
            home_id = teams_map.get(p1)
            away_id = teams_map.get(p2)

        match_obj = Match(
            match_id=m_id,
            home_team_id=uuid6.UUID(home_id) if home_id else None,
            away_team_id=uuid6.UUID(away_id) if away_id else None,
            scheduled_time=datetime.now(),  # Placeholder as original configs don't have time
            stage_id=stage_obj.stage_id,
            score=MatchScore.PENDING,
            detailed_score=None,
            has_ended=False
        )
        matches_list.append(match_obj)

    # 3. Create Tournament Object
    tournament_obj = Tournament(
        tournament_id=t_id,
        tournament_name=config.NAME,
        participating_teams=[uuid6.UUID(tid) for name, tid in teams_map.items() if name in config.TEAM_FLAGS],
        stages=list(stages_instances.values()),
        matches=matches_list,
        participating_users=set(),  # To be populated from users.json in next step
        private_brackets=[]
    )

    # 4. Save to JSON
    file_name = f"data/v2_local/{config.ID}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        # Using model_dump_json for Pydantic compatibility
        f.write(tournament_obj.model_dump_json(indent=4))

    print(f"✅ Created {file_name}")


if __name__ == "__main__":
    teams_lookup = load_teams_map()

    migrate_tournament(nba_cfg, NBA_TOURNAMENT_ID, "NBA", teams_lookup)
    migrate_tournament(ucl_cfg, UCL_TOURNAMENT_ID, "UCL", teams_lookup)