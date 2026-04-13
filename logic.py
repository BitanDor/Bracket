# TO EXECUTE: streamlit run app.py

NOT_DETERMINED = "TBD"

def get_effective_guesses(user_obj, config):
    effective = {k: v for k, v in user_obj.items() if not isinstance(v, dict)}
    for stage in config.STAGES[:-1]:
        bucket = f"corrections_after_{stage}"
        for m_id, val in user_obj.get(bucket, {}).items():
            effective[m_id] = val
    return effective


def get_guess_info(user_obj, m_id, config):
    for stage in reversed(config.STAGES[:-1]):
        bucket = f"corrections_after_{stage}"
        if m_id in user_obj.get(bucket, {}):
            return user_obj[bucket][m_id], stage
    return user_obj.get(m_id), "BASE"


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
                target_match = p_id[2:];
                want_loser = True
            elif p_id.startswith("W_"):
                target_match = p_id[2:]

            if target_match in config.TEAMS or target_match in config.BRACKET_STRUCTURE:
                # שימוש בקבוע במקום בעברית
                winner = actual_results.get(target_match) or effective_guesses.get(target_match)

                if not winner or winner == NOT_DETERMINED:
                    participants.append(NOT_DETERMINED)
                elif not want_loser:
                    participants.append(winner)
                else:
                    p_teams = get_participant_teams(target_match, effective_guesses, actual_results, config)
                    if NOT_DETERMINED in p_teams:
                        participants.append(NOT_DETERMINED)
                    else:
                        # השוואה בטוחה בין שמות קבוצות (באנגלית)
                        loser = [t for t in p_teams if t != winner]
                        participants.append(loser[0] if loser else NOT_DETERMINED)
            else:
                participants.append(p_id)
        return participants
    return [NOT_DETERMINED, NOT_DETERMINED]


def calculate_score(user_obj, actual_results, config):
    total_score = 0
    all_matches = list(config.TEAMS.keys()) + list(config.BRACKET_STRUCTURE.keys())

    for m_id in all_matches:
        actual_winner = actual_results.get(m_id)
        # שימוש בקבוע
        if not actual_winner or actual_winner == NOT_DETERMINED:
            continue

        guess_val, bucket = get_guess_info(user_obj, m_id, config)
        if guess_val == actual_winner:
            match_type = next((s for s in reversed(config.STAGES) if s in m_id), None)
            if not match_type and ("FINAL" in m_id or "FINALS" in m_id):
                match_type = "FINALS" if "FINALS" in config.STAGES else "FINAL"

            if match_type:
                total_score += config.POINTS_MAP.get(match_type, {}).get(bucket, 0)
    return total_score, {}