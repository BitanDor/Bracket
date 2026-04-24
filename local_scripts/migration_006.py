import json
import uuid6
from datetime import datetime
from typing import Dict, List, Optional
from domain.models import (
    Tournament, Stage, Match, StageType, DetailedScoreType,
    MatchScore, tournamentId,
    DependencySource, DependencyTarget, SourceType, SelectionRule
)
import tournaments.nba_2026_config as nba_cfg
import tournaments.ucl_2026_config as ucl_cfg

# Using the IDs we already established
NBA_TOURNAMENT_ID = uuid6.UUID("019dbbe0-fb87-7065-96f5-b4e509a4aa74")
UCL_TOURNAMENT_ID = uuid6.UUID("019dbbe0-fb86-771f-8c54-c3f07108f0b4")


def load_teams_map() -> Dict[str, str]:
    """Loads existing teams and maps their name to their established UUID."""
    with open("../data/v2_local/teams.json", "r", encoding="utf-8") as f:
        teams_data = json.load(f)
    return {details["team_name"]: tid for tid, details in teams_data.items()}


def create_stages(stage_names: List[str], tournament_type: str) -> Dict[str, Stage]:
    """Initializes Stage objects with correct scoring types."""
    stages_map = {}
    for stage_name in stage_names:
        stage_id = uuid6.uuid7()

        if tournament_type == "NBA":
            stage_category = StageType.PLAY_IN_STAGE if "PLAY_IN" in stage_name else StageType.PLAYOFF_STAGE
            score_format = DetailedScoreType.SERIES
        else:  # UCL
            stage_category = StageType.PLAYOFF_STAGE
            score_format = DetailedScoreType.DECISIVE if stage_name == "FINAL" else DetailedScoreType.HOME_AWAY

        stages_map[stage_name] = Stage(
            stage_id=stage_id,
            stage_name=stage_name,
            stage_type=stage_category,
            stage_possible_detailed_score=score_format
        )
    return stages_map


def build_tournament(config, tournament_id: tournamentId, tournament_type: str, teams_map: Dict[str, str]):
    print(f"🏗️ Building {config.NAME} from scratch with wiring...")

    stages_instances = create_stages(config.STAGES, tournament_type)

    # 1. First Pass: Create all match objects and store them by their config key (e.g., 'QF1')
    config_match_keys = list(config.TEAMS.keys()) + list(config.BRACKET_STRUCTURE.keys())
    config_match_keys = list(dict.fromkeys(config_match_keys))  # Remove duplicates

    match_registry: Dict[str, Match] = {}

    for match_key in config_match_keys:
        match_uuid = uuid6.uuid7()

        # Identify correct Stage
        assigned_stage_name = "UNKNOWN"
        for stage_name in config.STAGES:
            if match_key.startswith(stage_name) or stage_name in match_key:
                assigned_stage_name = stage_name
                break

        stage_object = stages_instances.get(assigned_stage_name)

        # Identify immediate participants if they are static teams
        participants = config.TEAMS.get(match_key) or config.BRACKET_STRUCTURE.get(match_key)
        home_team_uuid = teams_map.get(participants[0]) if participants else None
        away_team_uuid = teams_map.get(participants[1]) if participants else None

        match_registry[match_key] = Match(
            match_id=match_uuid,
            home_team_id=uuid6.UUID(home_team_uuid) if home_team_uuid else None,
            away_team_id=uuid6.UUID(away_team_uuid) if away_team_uuid else None,
            scheduled_time=datetime.now(),
            stage_id=stage_object.stage_id,
            score=MatchScore.PENDING,
            detailed_score=None,
            has_ended=False
        )

    # 2. Second Pass: Establish Wiring (Dependencies and Targets)
    for match_key, participants in config.BRACKET_STRUCTURE.items():
        current_match = match_registry[match_key]

        for index, source_key in enumerate(participants):
            # Check if the source is a reference to another match
            is_loser_rule = source_key.startswith("L_")
            actual_source_key = source_key[2:] if is_loser_rule else source_key

            if actual_source_key in match_registry:
                source_match = match_registry[actual_source_key]
                rule = SelectionRule.LOSER if is_loser_rule else SelectionRule.WINNER

                # Create Dependency Source (Input)
                dep_source = DependencySource(
                    source_id=source_match.match_id,
                    source_type=SourceType.MATCH,
                    rule=rule
                )

                if index == 0:
                    current_match.home_source = dep_source
                else:
                    current_match.away_source = dep_source

                # Create Dependency Target (Output)
                source_match.output_targets.append(DependencyTarget(
                    target_id=current_match.match_id,
                    target_slot="home" if index == 0 else "away",
                    rule=rule  # Added this line
                ))

    # 3. Assemble Tournament
    tournament_object = Tournament(
        tournament_id=tournament_id,
        tournament_name=config.NAME,
        participating_teams=[uuid6.UUID(tid) for name, tid in teams_map.items() if name in config.TEAM_FLAGS],
        stages=list(stages_instances.values()),
        groups=[],  # UCL/NBA currently don't use the new Group object in this config
        matches=list(match_registry.values()),
        participating_users=set(),
        private_brackets=[]
    )

    # 4. Save to JSON
    output_filename = f"data/v2_local/{config.ID}.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(tournament_object.model_dump_json(indent=4))

    print(f"✅ Created {output_filename} with full bidirectional wiring.")


if __name__ == "__main__":
    teams_lookup = load_teams_map()
    build_tournament(nba_cfg, NBA_TOURNAMENT_ID, "NBA", teams_lookup)
    build_tournament(ucl_cfg, UCL_TOURNAMENT_ID, "UCL", teams_lookup)