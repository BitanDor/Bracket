import json


def inspect_tournament(tournament_path, teams_path):
    # Load the unified teams database
    with open(teams_path, "r", encoding="utf-8") as f:
        teams_db = json.load(f)

    # Load the generated tournament blueprint
    with open(tournament_path, "r", encoding="utf-8") as f:
        tournament = json.load(f)

    print(f"\n=== Tournament Inspection: {tournament['tournament_name']} ===")
    print(f"ID: {tournament['tournament_id']}")

    # Create a mapping for stages for easier access
    stages_map = {s['stage_id']: s for s in tournament['stages']}

    # Group matches by stage for clear output
    matches_by_stage = {}
    for match in tournament['matches']:
        stage_id = match['stage_id']
        if stage_id not in matches_by_stage:
            matches_by_stage[stage_id] = []
        matches_by_stage[stage_id].append(match)

    # Print results
    for stage_id, matches in matches_by_stage.items():
        stage_name = stages_map[stage_id]['stage_name']
        print(f"\n--- Stage: {stage_name} ---")

        for match in matches:
            home_id = match.get('home_team_id')
            away_id = match.get('away_team_id')

            # Resolve team names or show TBD
            home_name = teams_db[home_id]['team_name'] if home_id else "TBD (From Prev Match)"
            away_name = teams_db[away_id]['team_name'] if away_id else "TBD (From Prev Match)"

            print(f"Match {match['match_id'][:8]}... : {home_name} vs {away_name}")


if __name__ == "__main__":
    # Inspect NBA
    inspect_tournament("../data/v2_local/nba_2026.json", "data/v2_local/teams.json")
    # Inspect UCL
    inspect_tournament("../data/v2_local/ucl_2026.json", "data/v2_local/teams.json")