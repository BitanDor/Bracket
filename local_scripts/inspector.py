import json
import os
import re

# Constant prefix for our UUID7s
UUID_PREFIX = "019db"
UUID_LENGTH = 36


def build_uuid_to_str_map():
    """
    Scans all local v2 data files to build a flat mapping between
    UUID strings and human-readable names.
    """
    mapping = {}
    base_path = "data/v2_local"

    # 1. Map Teams
    teams_path = os.path.join(base_path, "teams.json")
    if os.path.exists(teams_path):
        with open(teams_path, "r", encoding="utf-8") as f:
            teams = json.load(f)
            for tid, details in teams.items():
                mapping[tid] = f"TEAM:{details['team_name']}"

    # 2. Map Users
    users_path = os.path.join(base_path, "users.json")
    if os.path.exists(users_path):
        with open(users_path, "r", encoding="utf-8") as f:
            users = json.load(f)
            for uid, details in users.items():
                mapping[uid] = f"USER:{details['username']}"

    # 3. Map Tournaments, Stages, and Matches from tournament files
    tournament_files = ["nba_2026.json", "ucl_2026.json"]
    for t_file in tournament_files:
        path = os.path.join(base_path, t_file)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                t_data = json.load(f)

                # Tournament Name
                mapping[t_data['tournament_id']] = f"TOURNAMENT:{t_data['tournament_name']}"

                # Stage Names
                for stage in t_data.get('stages', []):
                    mapping[stage['stage_id']] = f"STAGE:{stage['stage_name']}"

                # Match Indicators with stage context
                for match in t_data.get('matches', []):
                    stage_id = match['stage_id']
                    stage_name = next((s['stage_name'] for s in t_data['stages'] if s['stage_id'] == stage_id),
                                      "Unknown")
                    mapping[match['match_id']] = f"MATCH_IN_{stage_name}"

    return mapping


def inspect_file(path_to_file):
    """
    Reads a file line by line and replaces UUIDs with human-readable strings
    plus a unique 4-character suffix from the UUID itself.
    """
    if not os.path.exists(path_to_file):
        print(f"Error: File {path_to_file} not found.")
        return

    uuid_map = build_uuid_to_str_map()

    # Regex to find our specific UUIDs starting with 019db
    uuid_pattern = re.compile(rf"{UUID_PREFIX}[a-f0-9\-]{{{UUID_LENGTH - len(UUID_PREFIX)}}}")

    print(f"\n--- Inspecting File: {path_to_file} ---")

    with open(path_to_file, "r", encoding="utf-8") as f:
        for line in f:
            line_content = line.rstrip()

            # Find all UUIDs in the current line
            matches = uuid_pattern.findall(line_content)

            # Replace each found UUID
            for uuid_str in matches:
                # Extract the 4-character suffix from the middle (index 19 to 23)
                short_id = uuid_str[19:23]

                readable_name = uuid_map.get(uuid_str)
                if readable_name:
                    # Format: <NAME_suffix>
                    replacement = f"<{readable_name}_{short_id}>"
                else:
                    # If ID is unknown, show the prefix and the suffix
                    replacement = f"<{uuid_str[:8]}..._{short_id} (Unknown)>"

                line_content = line_content.replace(uuid_str, replacement)

            print(line_content)


if __name__ == "__main__":
    inspect_file("data/v2_local/nba_2026.json")
    inspect_file("data/v2_local/ucl_2026.json")