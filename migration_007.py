import json
import uuid
import uuid6
from typing import List
from domain.models import Tournament, PrivateBracket

# Using standard uuid.UUID for constants to match the model expectation
NBA_TOURNAMENT_ID = uuid.UUID("019dbbe0-fb87-7065-96f5-b4e509a4aa74")
UCL_TOURNAMENT_ID = uuid.UUID("019dbbe0-fb86-771f-8c54-c3f07108f0b4")
DOR_USER_ID = uuid.UUID("019dbbe0-fb88-7250-9bd3-2eb71bbbd15b")


def load_users():
    with open("data/v2_local/users.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_tournament(file_name: str) -> Tournament:
    path = f"data/v2_local/{file_name}"
    with open(path, "r", encoding="utf-8") as f:
        # Enterprise best practice: use model_validate_json for automated coercion
        return Tournament.model_validate_json(f.read())


def save_json(data: dict, file_name: str):
    path = f"data/v2_local/{file_name}"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def migrate_participants_and_brackets():
    print("🚀 Starting migration 007: Participants and Private Brackets...")

    users_data = load_users()
    private_brackets_db = {}

    nba_usernames = ["Dor", "Alon", "Nir", "Maor"]
    ucl_usernames = ["Dor", "Alon", "Nir", "Shusha", "Ziv", "Galya", "Bob"]

    def get_user_uuids(username_list: List[str]) -> List[uuid.UUID]:
        # Explicitly converting string IDs to UUID objects
        return [uuid.UUID(uid) for uid, u in users_data.items() if u["username"] in username_list]

    # --- 1. Process NBA ---
    nba_tournament = load_tournament("nba_2026.json")
    nba_uuids = get_user_uuids(nba_usernames)

    nba_tournament.participating_users = set(nba_uuids)

    nba_bracket_id = uuid6.uuid7()  # Still using uuid7 for generation
    nba_bracket = PrivateBracket(
        bracket_id=nba_bracket_id,
        tournament_id=NBA_TOURNAMENT_ID,
        join_link="https://bracketmaster.streamlit.app/join/nba-private-v1",
        participants_ids=nba_uuids,
        manager_id=DOR_USER_ID,
        leaderboard={str(uid): 0 for uid in nba_uuids},
        whatsapp_group_connection_details=None
    )

    nba_tournament.private_brackets = [nba_bracket_id]
    private_brackets_db[str(nba_bracket_id)] = nba_bracket.model_dump(mode='json')

    # --- 2. Process UCL ---
    ucl_tournament = load_tournament("ucl_2026.json")
    ucl_uuids = get_user_uuids(ucl_usernames)

    ucl_tournament.participating_users = set(ucl_uuids)

    ucl_bracket_id = uuid6.uuid7()
    ucl_bracket = PrivateBracket(
        bracket_id=ucl_bracket_id,
        tournament_id=UCL_TOURNAMENT_ID,
        join_link="https://bracketmaster.streamlit.app/join/ucl-private-v1",
        participants_ids=ucl_uuids,
        manager_id=DOR_USER_ID,
        leaderboard={str(uid): 0 for uid in ucl_uuids},
        whatsapp_group_connection_details=None
    )

    ucl_tournament.private_brackets = [ucl_bracket_id]
    private_brackets_db[str(ucl_bracket_id)] = ucl_bracket.model_dump(mode='json')

    # --- 3. Save All Outputs ---
    with open("data/v2_local/nba_2026.json", "w", encoding="utf-8") as f:
        f.write(nba_tournament.model_dump_json(indent=4))

    with open("data/v2_local/ucl_2026.json", "w", encoding="utf-8") as f:
        f.write(ucl_tournament.model_dump_json(indent=4))

    save_json(private_brackets_db, "private_brackets.json")

    print(f"✅ NBA Tournament updated. Bracket ID: {nba_bracket_id}")
    print(f"✅ UCL Tournament updated. Bracket ID: {ucl_bracket_id}")


if __name__ == "__main__":
    migrate_participants_and_brackets()