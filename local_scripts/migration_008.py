import json
import os
from datetime import datetime

# --- CONFIGURATION: Define time windows for each stage name ---
# These represent the window BEFORE the stage begins.
NBA_TIME_WINDOWS = {
    "PLAY_IN_1": ("2026-04-10 00:00", "2026-04-12 23:59"),
    "PLAY_IN_2": ("2026-04-13 00:00", "2026-04-14 23:59"),
    "R1": ("2026-04-15 00:00", "2026-05-05 23:59"),
    "CONF_SEMIS": ("2026-05-06 00:00", "2026-05-20 23:59"),
    "CONF_FINALS": ("2026-05-21 00:00", "2026-06-05 23:59"),
    "FINALS": ("2026-06-06 00:00", "2026-06-25 23:59")
}

# The chronological order of stages for logic propagation
NBA_STAGE_ORDER = ["PLAY_IN_1", "PLAY_IN_2", "R1", "CONF_SEMIS", "CONF_FINALS", "FINALS"]

UCL_TIME_WINDOWS = {
    "R16": ("2026-02-10 00:00", "2026-03-18 23:59"),
    "QF": ("2026-04-07 00:00", "2026-04-16 23:59"),
    "SF": ("2026-04-28 00:00", "2026-05-07 23:59"),
    "FINAL": ("2026-05-08 00:00", "2026-05-30 23:59")
}

UCL_STAGE_ORDER = ["R16", "QF", "SF", "FINAL"]

DATA_DIR = "../data/v2_local"


def update_tournament_windows(file_name, window_config, stage_order):
    """
    Updates tournament matches with time windows that are valid ONLY up to
    the match's current stage.
    """
    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Applying logical time windows for: {data['tournament_name']}...")

    # Map Stage ID -> Stage Name for reverse lookup
    id_to_stage_name = {s['stage_id']: s['stage_name'] for s in data.get('stages', [])}
    # Map Stage Name -> Stage ID for building the match windows
    name_to_stage_id = {s['stage_name']: s['stage_id'] for s in data.get('stages', [])}

    for match in data.get('matches', []):
        match_stage_name = id_to_stage_name.get(match['stage_id'])
        if not match_stage_name:
            continue

        # Determine which stages are valid for this match (preceding and current)
        if match_stage_name in stage_order:
            current_stage_index = stage_order.index(match_stage_name)
            valid_stages = stage_order[:current_stage_index + 1]
        else:
            valid_stages = []

        # Create the specific window map for this match
        match_windows = {}
        for stage_name in valid_stages:
            if stage_name in window_config and stage_name in name_to_stage_id:
                s_id = name_to_stage_id[stage_name]
                match_windows[s_id] = window_config[stage_name]

        match['match_guess_time_windows'] = match_windows

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Successfully updated {file_name} with chronological windows.")


if __name__ == "__main__":
    # Update NBA with chronological filtering
    update_tournament_windows("nba_2026.json", NBA_TIME_WINDOWS, NBA_STAGE_ORDER)

    # Update UCL with chronological filtering
    update_tournament_windows("ucl_2026.json", UCL_TIME_WINDOWS, UCL_STAGE_ORDER)