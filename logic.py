# logic.py

def get_effective_guesses(user_obj, config):
    effective = {k: v for k, v in user_obj.items() if not isinstance(v, dict)}

    # שימוש גנרי ברשימת השלבים מתוך קובץ התחרות
    for stage in config.STAGES[:-1]:
        bucket = f"corrections_after_{stage}"
        for m_id, val in user_obj.get(bucket, {}).items():
            effective[m_id] = val
    return effective


def get_guess_info(user_obj, m_id, config):
    # סריקה לאחור של השלבים כדי למצוא את התיקון המאוחר ביותר
    for stage in reversed(config.STAGES[:-1]):
        bucket = f"corrections_after_{stage}"
        if m_id in user_obj.get(bucket, {}):
            return user_obj[bucket][m_id], stage
    return user_obj.get(m_id), "BASE"


def get_participant_teams(match_id, effective_guesses, actual_results, config):
    """קובעת מי משחק בכל משחק. תומכת במנצחות (W_), מפסידות (L_) ושמות קבוצות קבועים."""

    # 1. אם המשחק מוגדר ב-BRACKET_STRUCTURE (משחק עם תלויות או שמות מעורבים)
    if match_id in config.BRACKET_STRUCTURE:
        parent_ids = config.BRACKET_STRUCTURE.get(match_id, [])
        participants = []

        for p_id in parent_ids:
            target_match = p_id
            want_loser = False

            # זיהוי בקשה למנצחת/מפסידה
            if p_id.startswith("L_"):
                target_match = p_id[2:]
                want_loser = True
            elif p_id.startswith("W_"):
                target_match = p_id[2:]

            # בדיקה האם המזהה הוא משחק קיים או שם של קבוצה
            is_match = (target_match in config.TEAMS or target_match in config.BRACKET_STRUCTURE)

            if is_match:
                # אם זה משחק - ננסה להביא את המנצחת/מפסידה
                winner = actual_results.get(target_match) or effective_guesses.get(target_match)
                if not winner or winner == "TBD":
                    participants.append("TBD")
                elif not want_loser:
                    participants.append(winner)
                else:
                    # לוגיקת חילוץ מפסידה
                    teams_in_target = get_participant_teams(target_match, effective_guesses, actual_results, config)
                    if "TBD" in teams_in_target:
                        participants.append("TBD")
                    else:
                        loser = [t for t in teams_in_target if t != winner]
                        participants.append(loser[0] if loser else "TBD")
            else:
                # אם זה לא משחק - זה כנראה שם של קבוצה קבועה (כמו Detroit Pistons)
                participants.append(p_id)
        return participants

    # 2. אם המשחק מוגדר רק ב-TEAMS (שלב הבסיס)
    if match_id in config.TEAMS:
        return config.TEAMS.get(match_id, ["TBD", "TBD"])

    return ["TBD", "TBD"]


def calculate_score(user_obj, actual_results, config):
    total_score = 0
    breakdown = {}
    all_matches = list(config.TEAMS.keys()) + list(config.BRACKET_STRUCTURE.keys())

    for m_id in all_matches:
        actual_winner = actual_results.get(m_id)
        if not actual_winner: continue

        guess_val, bucket = get_guess_info(user_obj, m_id, config)

        if guess_val == actual_winner:
            match_type = m_id.split('_')[0] if '_' in m_id else m_id
            for stage in config.STAGES:
                if stage in match_type: match_type = stage

            points = config.POINTS_MAP.get(match_type, {}).get(bucket, 0)
            total_score += points
            breakdown[m_id] = points

    return total_score, breakdown


def get_eliminated_teams(actual_results, config):
    eliminated_teams = set()
    for m_id, winner in actual_results.items():
        participants = get_participant_teams(m_id, {}, actual_results, config)
        for team in participants:
            if team != "TBD" and team != winner:
                eliminated_teams.add(team)
    return eliminated_teams