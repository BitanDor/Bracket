# ui_components.py
import logic

def format_team(team_name, winner_node, config):
    # תרגום לצורכי תצוגה בלבד
    if team_name == logic.NOT_DETERMINED: return "<i>TBD</i>"
    flag = config.TEAM_FLAGS.get(team_name, "")
    style = "font-weight: bold;" if team_name == winner_node else ""
    star = " 🌟" if team_name == winner_node else ""
    return f"<span style='{style}'>{flag} {team_name}{star}</span>"


def get_match_box_html(m_id, winner_node, is_actual_view, raw_user_obj, config, current_guesses, actual_results):
    participants = logic.get_participant_teams(m_id, current_guesses, actual_results, config)
    team_a, team_b = participants[0], participants[1]
    actual_winner = actual_results.get(m_id)

    match_body = f"<div style='line-height: 1.1;'><br>{format_team(team_a, winner_node, config)}<br><small>vs</small><br>{format_team(team_b, winner_node, config)}</div>"

    bg_color, border_color, text_color = "#1976d2", "#1565c0", "white"
    status_msg = ""

    if not is_actual_view:
        # קבלת היסטוריית הניחושים
        _, bucket, prev_val = logic.get_guess_info(raw_user_obj, m_id, config)

        # א. האם זה תיקון? (כל מה שהוא לא BASE)
        if bucket != "BASE":
            bg_color, border_color, text_color = "#1e3a8a", "#3b82f6", "#ffaa00"  # כחול כהה
            status_msg = f"<div style='color: #ffaa00; font-size: 0.85em; margin-top:4px; font-weight: bold;'>⚠️ Corrected. Prev: {prev_val}</div>"

        # ב. בדיקה האם המשחק הסתיים (דריסת צבעים לירוק/אדום)
        if actual_winner and actual_winner != logic.NOT_DETERMINED:
            if winner_node == actual_winner:
                bg_color, border_color = "#2e7d32", "#1b5e20"
            else:
                bg_color, border_color = "#c62828", "#b71c1c"
        else:
            # ג. משחק עתידי - בדיקת היתכנות
            if winner_node != logic.NOT_DETERMINED and winner_node not in participants:
                bg_color, border_color = "#1a1a1a", "#444"
                status_msg = f"<div style='color: #ff4b4b; font-size: 0.8em; line-height: 1;'>❌ fix required <br><small>(You guessed:: {winner_node})</small></div>"

    return f"""<div style="background-color: {bg_color}; color: {text_color}; padding: 3px; border-radius: 3px; border: 1px solid {border_color}; margin-bottom: 1em; min-height: 6em; overflow: hidden; text-align: right;">
        {match_body}{status_msg}</div>"""