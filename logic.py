# logic.py
from constants import BRACKET_STRUCTURE, ROUND_POINTS, TEAMS


def get_effective_guesses(user_obj):
    """
    מקבל את אובייקט המשתמש השלם ומחזיר מילון שטוח של הניחושים התקפים כרגע.
    תיקונים מאוחרים דורסים ניחושים מוקדמים.
    """
    # 1. טעינת ניחושי הבסיס (המקוריים)
    effective = {k: v for k, v in user_obj.items() if not isinstance(v, dict)}

    # 2. דריסה לפי סדר כרונולוגי של התיקונים
    for bucket in ["corrections_after_R16", "corrections_after_QF", "corrections_after_SF"]:
        for m_id, val in user_obj.get(bucket, {}).items():
            effective[m_id] = val

    return effective


def get_guess_info(user_obj, m_id):
    """
    מחזיר את הניחוש התקף ואת השלב (Bucket) שבו הוא עודכן לאחרונה.
    """
    if m_id in user_obj.get("corrections_after_SF", {}): return user_obj["corrections_after_SF"][m_id], "SF"
    if m_id in user_obj.get("corrections_after_QF", {}): return user_obj["corrections_after_QF"][m_id], "QF"
    if m_id in user_obj.get("corrections_after_R16", {}): return user_obj["corrections_after_R16"][m_id], "R16"
    return user_obj.get(m_id), "BASE"


def get_participant_teams(match_id, effective_guesses, actual_results):
    """קובעת מי משחק בכל משחק, משתמשת בניחושים התקפים"""
    if match_id.startswith("R16"):
        return TEAMS.get(match_id, ["TBD", "TBD"])

    parent_matches = BRACKET_STRUCTURE.get(match_id, [])
    participants = []

    for parent_id in parent_matches:
        winner = actual_results.get(parent_id) or effective_guesses.get(parent_id)
        participants.append(winner if winner else "TBD")

    return participants


def calculate_score(user_obj, actual_results):
    """
    מחשבת את הניקוד לפי מפת נקודות (POINTS_MAP) שנגזרת מהמבנה שהצעת.
    """
    # מפת ניקוד: אם משחק X תוקן בשלב Y, כמה נקודות הוא שווה?
    POINTS_MAP = {
        "FINAL": {"BASE": 8, "R16": 4, "QF": 2, "SF": 1},
        "SF": {"BASE": 4, "R16": 2, "QF": 1},
        "QF": {"BASE": 2, "R16": 1},
        "R16": {"BASE": 1}
    }

    total_score = 0
    breakdown = {}

    all_matches = list(TEAMS.keys()) + list(BRACKET_STRUCTURE.keys())

    for m_id in all_matches:
        actual_winner = actual_results.get(m_id)
        if not actual_winner:
            continue

        guess_val, bucket = get_guess_info(user_obj, m_id)

        if guess_val == actual_winner:
            # זיהוי סוג המשחק
            match_type = m_id.split('_')[0] if '_' in m_id else m_id
            if "QF" in match_type:
                match_type = "QF"
            elif "SF" in match_type:
                match_type = "SF"

            points = POINTS_MAP.get(match_type, {}).get(bucket, 0)
            total_score += points
            breakdown[m_id] = points

    return total_score, breakdown


def get_eliminated_teams(actual_results):
    eliminated_teams = set()
    for m_id, winner in actual_results.items():
        participants = get_participant_teams(m_id, {}, actual_results)
        for team in participants:
            if team != "TBD" and team != winner:
                eliminated_teams.add(team)
    return eliminated_teams