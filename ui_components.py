# TO EXECUTE: streamlit run app.py

import logic


def format_team(team_name, winner_node, config):
    # winner_node יכול להיות מחרוזת או מערך [team, score]
    winner_name = logic.get_winner_name(winner_node)

    if team_name == logic.NOT_DETERMINED: return "<i>TBD</i>"
    flag = config.TEAM_FLAGS.get(team_name, "")
    style = "font-weight: bold;" if team_name == winner_name else ""
    star = " 🌟" if team_name == winner_name else ""
    return f"<span style='{style}'>{flag} {team_name}{star}</span>"


def get_match_box_html(m_id, winner_node, is_actual_view, raw_user_obj, config, current_guesses, actual_results):
    participants = logic.get_participant_teams(m_id, current_guesses, actual_results, config)
    team_a, team_b = participants[0], participants[1]

    # נרמול תוצאת האמת והניחוש הנוכחי
    actual_val_raw = actual_results.get(m_id)
    actual_winner_name = logic.get_winner_name(actual_val_raw)
    winner_name = logic.get_winner_name(winner_node)

    match_body = f"<div style='line-height: 1.1;'><br>{format_team(team_a, winner_node, config)}<br><small>vs</small><br>{format_team(team_b, winner_node, config)}</div>"

    bg_color, border_color, text_color = "#1976d2", "#1565c0", "white"
    status_msg = ""

    if not is_actual_view:
        # קבלת היסטוריית הניחושים ונרמול הערך הקודם
        _, bucket, prev_val_raw = logic.get_guess_info(raw_user_obj, m_id, config)
        prev_val_name = logic.get_winner_name(prev_val_raw)

        # א. האם זה תיקון?
        if bucket != "BASE":
            bg_color, border_color, text_color = "#1e3a8a", "#3b82f6", "#ffaa00"
            status_msg = f"<div style='color: #ffaa00; font-size: 0.85em; margin-top:4px; font-weight: bold;'>⚠️ Corrected. Prev: {prev_val_name}</div>"

        # ב. בדיקת תוצאה (השוואת שמות בלבד לצורך צבע התיבה)
        if actual_winner_name and actual_winner_name != logic.NOT_DETERMINED:
            if winner_name == actual_winner_name:
                bg_color, border_color = "#2e7d32", "#1b5e20"
            else:
                bg_color, border_color = "#c62828", "#b71c1c"
        else:
            # ג. משחק עתידי - בדיקת היתכנות
            if winner_name != logic.NOT_DETERMINED and winner_name not in participants:
                bg_color, border_color = "#1a1a1a", "#444"
                status_msg = f"<div style='color: #ff4b4b; font-size: 0.8em; line-height: 1;'>❌ fix required <br><small>(You guessed:: {winner_name})</small></div>"

    return f"""<div style="background-color: {bg_color}; color: {text_color}; padding: 3px; border-radius: 3px; border: 1px solid {border_color}; margin-bottom: 1em; min-height: 6em; overflow: hidden; text-align: right;">
        {match_body}{status_msg}</div>"""