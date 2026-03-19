# logic.py
from constants import BRACKET_STRUCTURE, ROUND_POINTS, TEAMS


def get_participant_teams(match_id, user_guesses, actual_results):
    """
    קובעת מי משחק בכל משחק.
    עבור שמינית - לוקח מ-constants.
    עבור שלבים מתקדמים - בודק מי המנצחות של השלבים הקודמים (אמת או ניחוש).
    """
    if match_id.startswith("R16"):
        return TEAMS.get(match_id, ["TBD", "TBD"])

    parent_matches = BRACKET_STRUCTURE.get(match_id, [])
    participants = []

    for parent_id in parent_matches:
        # עדיפות לתוצאת אמת. אם אין - לניחוש המשתמש. אם אין - TBD.
        winner = actual_results.get(parent_id) or user_guesses.get(parent_id)
        participants.append(winner if winner else "TBD")

    return participants


def get_original_planned_winner(match_id, user_guesses):
    """
    מזהה איזו קבוצה המשתמש תכנן שתגיע למשחק הזה במקור
    (לפי הניחושים שלו בשלב הקודם).
    """
    if match_id.startswith("R16"):
        return None

    parents = BRACKET_STRUCTURE.get(match_id, [])
    # נחזיר את שתי המנצחות שהמשתמש ניחש בשלב הקודם עבור הענף הזה
    planned_from_parents = [user_guesses.get(p) for p in parents if user_guesses.get(p)]
    return planned_from_parents


def get_streak_length(match_id, user_guesses, actual_results):
    """
    חישוב אורך הרצף העקבי והנכון של המשתמש.
    """
    user_winner = user_guesses.get(match_id)
    actual_winner = actual_results.get(match_id)

    # אם הניחוש שגוי או שאין עדיין תוצאה - אין רצף
    if not actual_winner or user_winner != actual_winner:
        return -1

        # שמינית גמר היא תמיד תחילת רצף (חזקה 0 = 1 נקודה)
    if match_id.startswith("R16"):
        return 0

    # חיפוש משחק המקור (מאיזה ענף הקבוצה הגיעה)
    parents = BRACKET_STRUCTURE.get(match_id, [])
    parent_match_id = None

    for p in parents:
        if user_guesses.get(p) == user_winner:
            parent_match_id = p
            break

    # אם המשתמש תיקן (החליף קבוצה ברבע למרות שלא ניחש שהיא תעלה מהשמינית)
    if parent_match_id is None:
        return 0

    prev_streak = get_streak_length(parent_match_id, user_guesses, actual_results)

    # אם השלב הקודם היה טעות, התיקון הנוכחי מתחיל רצף חדש מ-0
    if prev_streak == -1:
        return 0

    return 1 + prev_streak


def calculate_score(user_guesses, actual_results):
    """
    מחשבת את הניקוד הכולל ואת הפירוט לכל משחק.
    """
    total_score = 0
    breakdown = {}

    # רשימה של כל המשחקים בטורניר
    all_matches = list(TEAMS.keys()) + list(BRACKET_STRUCTURE.keys())

    for match_id in all_matches:
        streak = get_streak_length(match_id, user_guesses, actual_results)

        if streak >= 0:
            match_points = 2 ** streak
            total_score += match_points
            breakdown[match_id] = match_points

    return total_score, breakdown


def get_eliminated_teams(actual_results):
    """
    מזהה אילו קבוצות הודחו מהטורניר במציאות.
    """
    eliminated_teams = set()
    for m_id, winner in actual_results.items():
        participants = get_participant_teams(m_id, {}, actual_results)
        for team in participants:
            if team != "TBD" and team != winner:
                eliminated_teams.add(team)
    return eliminated_teams