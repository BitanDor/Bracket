import json
import uuid6
from typing import Dict, List, Optional
from domain.models import (
    Tournament, Match, DependencySource, DependencyTarget,
    SourceType, SelectionRule, matchId, groupId
)
import tournaments.nba_2026_config as nba_cfg
import tournaments.ucl_2026_config as ucl_cfg

# Re-using the same IDs
NBA_TOURNAMENT_ID = uuid6.UUID("019dbbe0-fb87-7065-96f5-b4e509a4aa74")
UCL_TOURNAMENT_ID = uuid6.UUID("019dbbe0-fb86-771f-8c54-c3f07108f0b4")


def load_tournament_file(file_path: str) -> Tournament:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Tournament.model_validate(data)


def wire_tournament(tournament: Tournament, config, teams_map: Dict[str, str]):
    print(f"🔗 Wiring {tournament.tournament_name}...")

    # 1. Map config keys to existing Match UUIDs
    # We use the fact that matches were created in the same order as config keys
    config_match_keys = list(config.TEAMS.keys()) + list(config.BRACKET_STRUCTURE.keys())
    config_match_keys = list(dict.fromkeys(config_match_keys))  # Deduplicate

    key_to_uuid: Dict[str, matchId] = {}
    for i, key in enumerate(config_match_keys):
        if i < len(tournament.matches):
            key_to_uuid[key] = tournament.matches[i].match_id

    # 2. Process Wiring
    for m_key, participants in config.BRACKET_STRUCTURE.items():
        current_match_id = key_to_uuid[m_key]
        current_match = next(m for m in tournament.matches if m.match_id == current_match_id)

        # We assume index 0 is home, index 1 is away
        sources = [participants[0], participants[1]]

        for idx, source_key in enumerate(sources):
            # If the source is another match key
            if source_key in key_to_uuid:
                source_match_id = key_to_uuid[source_key]
                rule = SelectionRule.WINNER

                # Special NBA Logic: Loser of Play-in 7vs8 goes to Play-in 2
                if source_key.startswith("L_"):
                    actual_source_key = source_key[2:]  # Remove 'L_'
                    source_match_id = key_to_uuid[actual_source_key]
                    rule = SelectionRule.LOSER

                # Create the DependencySource
                dep_source = DependencySource(
                    source_id=source_match_id,
                    source_type=SourceType.MATCH,
                    rule=rule
                )

                # Assign to slot
                if idx == 0:
                    current_match.home_source = dep_source
                else:
                    current_match.away_source = dep_source

                # Add Output Target to the source match (Bidirectional Wiring)
                source_match = next(m for m in tournament.matches if m.match_id == source_match_id)
                source_match.output_targets.append(DependencyTarget(
                    target_id=current_match_id,
                    target_slot="home" if idx == 0 else "away"
                ))

    # 3. Save updated tournament
    output_path = f"data/v2_local/{config.ID}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tournament.model_dump_json(indent=4))
    print(f"✅ Successfully wired {output_path}")


def load_teams_reverse_map():
    with open("data/v2_local/teams.json", "r", encoding="utf-8") as f:
        teams_data = json.load(f)
    return {details["team_name"]: tid for tid, details in teams_data.items()}


if __name__ == "__main__":
    teams_map = load_teams_reverse_map()

    # Wire NBA
    nba_tournament = load_tournament_file("data/v2_local/nba_2026.json")
    wire_tournament(nba_tournament, nba_cfg, teams_map)

    # Wire UCL
    ucl_tournament = load_tournament_file("data/v2_local/ucl_2026.json")
    wire_tournament(ucl_tournament, ucl_cfg, teams_map)