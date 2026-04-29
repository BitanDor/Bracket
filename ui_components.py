# TO EXECUTE: streamlit run app.py

import logic


def format_team(team_name, winner_name, series_score, config):
    # series_score מוצג רק כשקיימת תוצאה מדויקת תקינה
    if team_name == logic.NOT_DETERMINED: return "<i>TBD</i>"
    flag = config.TEAM_FLAGS.get(team_name, "")
    score_suffix = f" ({series_score})" if series_score is not None else ""
    style = "font-weight: bold;" if team_name == winner_name else ""
    star = " 🌟" if team_name == winner_name else ""
    return f"<span style='{style}'>{flag} {team_name}{score_suffix}{star}</span>"


def get_match_box_html(m_id, winner_node, is_actual_view, raw_user_obj, config, current_guesses, actual_results):
    participants = logic.get_participant_teams(m_id, current_guesses, actual_results, config)
    team_a, team_b = participants[0], participants[1]

    # נרמול תוצאת האמת והניחוש הנוכחי
    actual_val_raw = actual_results.get(m_id)
    actual_winner_name = logic.get_winner_name(actual_val_raw)
    winner_name = logic.get_winner_name(winner_node)
    winner_exact_games = logic.get_winner_result(winner_node)

    exact_enabled = getattr(config, "IS_EXACT_ENABLED", False)
    exact_options = getattr(config, "EXACT_OPTIONS", [4, 5, 6, 7])
    is_play_in_match = m_id.startswith("PLAY_IN")
    is_concluded_match = actual_winner_name and actual_winner_name != logic.NOT_DETERMINED

    # בתצוגות עם תוצאה מדויקת: מנצחת תמיד עם 4, המפסידה = total_games - 4
    show_series_scores = (
        exact_enabled
        and not is_play_in_match
        and winner_name
        and winner_name != logic.NOT_DETERMINED
        and winner_name in participants
        and winner_exact_games in exact_options
    )

    winner_series_score = 4 if show_series_scores else None
    loser_series_score = (winner_exact_games - 4) if show_series_scores else None

    team_a_score = None
    if show_series_scores and team_a != logic.NOT_DETERMINED:
        team_a_score = winner_series_score if team_a == winner_name else loser_series_score

    team_b_score = None
    if show_series_scores and team_b != logic.NOT_DETERMINED:
        team_b_score = winner_series_score if team_b == winner_name else loser_series_score

    match_body = f"<div style='line-height: 1.1;'><br>{format_team(team_a, winner_name, team_a_score, config)}<br><small>vs</small><br>{format_team(team_b, winner_name, team_b_score, config)}</div>"

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
        if is_concluded_match:
            if winner_name == actual_winner_name:
                bg_color, border_color = "#2e7d32", "#1b5e20"

                # ניחוש מדויק: גם מנצחת וגם מספר משחקים נכון
                actual_exact_games = logic.get_winner_result(actual_val_raw)
                is_exact_hit = (
                    exact_enabled
                    and not is_play_in_match
                    and actual_exact_games in exact_options
                    and winner_exact_games == actual_exact_games
                )
                if is_exact_hit:
                    border_color = "#f5c542"
                    status_msg += "<div style='color: #ffe082; font-size: 0.85em; margin-top:4px; font-weight: bold;'>✨ EXACT!</div>"
                elif exact_enabled and not is_play_in_match and actual_exact_games in exact_options:
                    # סדר תצוגה: קודם הקבוצה העליונה, ואז התחתונה
                    top_score = 4 if team_a == actual_winner_name else (actual_exact_games - 4)
                    bottom_score = 4 if team_b == actual_winner_name else (actual_exact_games - 4)
                    status_msg += f"<div style='color: #dcedc8; font-size: 0.85em; margin-top:4px; font-weight: bold;'>True score: {top_score}:{bottom_score}</div>"
            else:
                bg_color, border_color = "#c62828", "#b71c1c"
        else:
            # ג. משחק עתידי - בדיקת היתכנות
            if winner_name != logic.NOT_DETERMINED and winner_name not in participants:
                bg_color, border_color = "#1a1a1a", "#444"
                status_msg = f"<div style='color: #ff4b4b; font-size: 0.8em; line-height: 1;'>❌ fix required <br><small>(You guessed:: {winner_name})</small></div>"

    return f"""<div style="background-color: {bg_color}; color: {text_color}; padding: 3px; border-radius: 3px; border: 1px solid {border_color}; margin-bottom: 1em; min-height: 6em; overflow: hidden; text-align: right;">
        {match_body}{status_msg}</div>"""