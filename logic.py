# logic.py

NOT_DETERMINED = "TBD"


# --- שכבת נרמול הנתונים ---

def get_winner_name(val):
    """מחזירה את שם הקבוצה מתוך הערך (תומכת במחרוזת או ברשימה)"""
    if isinstance(val, list) and len(val) > 0:
        return val[0]
    return val


def get_winner_result(val):
    """מחזירה את התוצאה (מספר משחקים) מתוך הערך או None"""
    if isinstance(val, list) and len(val) > 1:
        return val[1]
    return None


# ---------------------------

def get_effective_guesses(user_obj, config):
    effective = {k: v for k, v in user_obj.items() if not isinstance(v, dict)}
    for stage in config.STAGES[:-1]:
        bucket = f"corrections_after_{stage}"
        for m_id, val in user_obj.get(bucket, {}).items():
            effective[m_id] = val
    return effective


def get_guess_info(user_obj, m_id, config):
    current_val = None
    last_bucket_stage = "BASE"
    previous_val = None
    found_current = False

    for stage in reversed(config.STAGES[:-1]):
        bucket = f"corrections_after_{stage}"
        if m_id in user_obj.get(bucket, {}):
            if not found_current:
                current_val = user_obj[bucket][m_id]
                last_bucket_stage = stage
                found_current = True
            else:
                previous_val = user_obj[bucket][m_id]
                break

    if not found_current:
        current_val = user_obj.get(m_id)
    elif previous_val is None:
        previous_val = user_obj.get(m_id)

    return current_val, last_bucket_stage, previous_val


def calculate_score(user_obj, actual_results, config):
    total_score = 0
    all_matches = list(config.TEAMS.keys()) + list(config.BRACKET_STRUCTURE.keys())

    # בדיקה האם הטורניר תומך בתוצאה מדויקת (בדיקה בטוחה)
    exact_enabled = getattr(config, "IS_EXACT_ENABLED", False)

    for m_id in all_matches:
        actual_val_raw = actual_results.get(m_id)
        actual_team = get_winner_name(actual_val_raw)

        if not actual_team or actual_team == NOT_DETERMINED:
            continue

        guess_val_raw, bucket, _ = get_guess_info(user_obj, m_id, config)
        guess_team = get_winner_name(guess_val_raw)

        if guess_team == actual_team:
            match_type = next((s for s in reversed(config.STAGES) if s in m_id), None)
            if not match_type and ("FINAL" in m_id or "FINALS" in m_id):
                match_type = "FINALS" if "FINALS" in config.STAGES else "FINAL"

            if match_type:
                stage_points_map = config.POINTS_MAP.get(match_type, {})

                # חישוב ניקוד בסיס לפי באקט
                points = 0
                if bucket in stage_points_map:
                    points = stage_points_map[bucket]
                else:
                    if bucket == "BASE":
                        points = stage_points_map.get("BASE", 0)
                    else:
                        found_pts = 0
                        for s in config.STAGES:
                            if s in stage_points_map:
                                found_pts = stage_points_map[s]
                            if s == bucket:
                                break
                        points = found_pts

                # --- הכפלה ב-3 עבור תוצאה מדויקת ---
                if exact_enabled:
                    actual_score = get_winner_result(actual_val_raw)
                    guess_score = get_winner_result(guess_val_raw)
                    if actual_score is not None and actual_score == guess_score:
                        points *= 3

                total_score += points

    return total_score, {}


def get_participant_teams(match_id, effective_guesses, actual_results, config):
    if match_id in config.TEAMS:
        return config.TEAMS[match_id]

    if match_id in config.BRACKET_STRUCTURE:
        parent_ids = config.BRACKET_STRUCTURE[match_id]
        participants = []
        for p_id in parent_ids:
            target_match = p_id
            want_loser = False
            if p_id.startswith("L_"):
                target_match = p_id[2:]
                want_loser = True
            elif p_id.startswith("W_"):
                target_match = p_id[2:]

            if target_match in config.TEAMS or target_match in config.BRACKET_STRUCTURE:
                # שימוש בנרמול שמות עבור הרקורסיה
                actual_raw = actual_results.get(target_match)
                actual_team = get_winner_name(actual_raw)

                if actual_team and actual_team != NOT_DETERMINED:
                    winner = actual_team
                else:
                    guess_raw = effective_guesses.get(target_match)
                    winner = get_winner_name(guess_raw)

                if not winner or winner == NOT_DETERMINED:
                    participants.append(NOT_DETERMINED)
                else:
                    parent_participants = get_participant_teams(target_match, effective_guesses, actual_results, config)

                    if winner in parent_participants:
                        if not want_loser:
                            participants.append(winner)
                        else:
                            loser = [t for t in parent_participants if t != winner]
                            participants.append(loser[0] if loser else NOT_DETERMINED)
                    else:
                        participants.append(NOT_DETERMINED)
            else:
                participants.append(p_id)
        return participants
    return [NOT_DETERMINED, NOT_DETERMINED]