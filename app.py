# app.py
import streamlit as st
import pandas as pd
import logic
import data_manager
from tournaments import ucl_2026_config, nba_2026_config

AVAILABLE_TOURNAMENTS = {
    ucl_2026_config.ID: ucl_2026_config,
    nba_2026_config.ID: nba_2026_config
}


def main():
    st.set_page_config(page_title="Bitan's Bracket", layout="wide", page_icon="🏆")

    # תפריט בחירת תחרות (ממוקם למעלה)
    col1, col2 = st.columns([1, 4])
    with col1:
        comp_id = st.selectbox("בחר תחרות:", list(AVAILABLE_TOURNAMENTS.keys()),
                               format_func=lambda x: AVAILABLE_TOURNAMENTS[x].NAME)

    config = AVAILABLE_TOURNAMENTS[comp_id]
    st.title(f"Bitan's Bracket - {config.NAME} 🏆")

    # טעינת נתונים לתחרות הנבחרת
    all_guesses = data_manager.load_all_guesses(comp_id)
    actual_results = data_manager.load_actual_results(comp_id)

    # --- sidebar: טבלת ניקוד ---
    st.sidebar.header("📊 טבלת ניקוד")
    leaderboard_data = []
    for user, user_obj in all_guesses.items():
        score, _ = logic.calculate_score(user_obj, actual_results, config)
        effective_guesses = logic.get_effective_guesses(user_obj, config)

        predicted_winner = effective_guesses.get("FINAL", "TBD")
        flag = config.TEAM_FLAGS.get(predicted_winner, "")
        winner_display = f"{flag} {predicted_winner}" if predicted_winner != "TBD" else "TBD"

        leaderboard_data.append({"שם": user, "זוכה": winner_display, "נקודות": score})

    if leaderboard_data:
        df = pd.DataFrame(leaderboard_data).sort_values(by="נקודות", ascending=False)
        df = df[["שם", "זוכה", "נקודות"]]
        df.index = range(1, len(df) + 1)
        df.index.name = "מיקום"
        st.sidebar.table(df)
    else:
        st.sidebar.write("עוד אין ניחושים.")

    # --- טאבים בממשק הראשי ---
    tab_tree, tab_add, tab_admin = st.tabs(["🌳 עץ הטורניר", "✍️ ניהול ניחושים", "⚙️ תוצאות אמת"])

    with tab_tree:
        st.header(" 🌳 עץ הטורניר")
        view_user = st.selectbox("בחר חבר כדי לראות את העץ שלו:", ["תוצאות אמת"] + list(all_guesses.keys()))

        is_actual_view = (view_user == "תוצאות אמת")
        raw_user_obj = {} if is_actual_view else all_guesses.get(view_user, {})
        current_display_guesses = actual_results if is_actual_view else logic.get_effective_guesses(raw_user_obj,
                                                                                                    config)

        eliminated_teams = logic.get_eliminated_teams(actual_results, config)

        def format_team(team_name, is_winner_node):
            if team_name == "TBD": return "<i>TBD</i>"
            flag = config.TEAM_FLAGS.get(team_name, "")
            prefix_icon = " 🌟" if team_name == is_winner_node else ""
            style = "font-weight: bold;" if team_name == is_winner_node else ""
            return f"<span style='{style}'>{flag} {team_name}{prefix_icon}</span>"

        def get_spacer_html(em_height):
            return f"<div style='height: {em_height}em;'></div>"

        def get_match_box_html(m_id, winner_node, user_eliminated_node, actual_w_node, is_actual_view, raw_user_obj,
                               config):
            participants = logic.get_participant_teams(m_id, current_display_guesses, actual_results, config)
            team_a, team_b = participants[0], participants[1]

            match_html = f"<div style='line-height: 1.1;'><br>{format_team(team_a, winner_node)}<br><small>vs</small><br>{format_team(team_b, winner_node)}</div>"

            is_corrected = False
            if not is_actual_view and raw_user_obj:
                _, bucket = logic.get_guess_info(raw_user_obj, m_id, config)
                if bucket != "BASE":
                    is_corrected = True
                    original_guess = raw_user_obj.get(m_id, "???")
                    match_html += f"<div style='color: #ffaa00; font-size: 0.85em; margin-top:4px; font-weight: bold;'>⚠️ תוקן (במקור: {original_guess})</div>"

            bg_color, border_color, text_color = "#1976d2", "#1565c0", "white"

            if not is_actual_view:
                if actual_w_node:
                    if winner_node == actual_w_node:
                        bg_color, border_color = "#2e7d32", "#1b5e20"
                    else:
                        bg_color, border_color = "#c62828", "#b71c1c"
                elif winner_node in user_eliminated_node:
                    bg_color, border_color = "#1a1a1a", "#444"
                    match_html += "<div style='color: #ff4b4b; font-size: 0.8em; line-height: 1;'>❌ הודחה - דורש תיקון</div>"
                elif is_corrected:
                    bg_color, border_color, text_color = "#1e3a8a", "#3b82f6", "#ffaa00"

            return f"""<div style="background-color: {bg_color}; color: {text_color}; padding: 3px; border-radius: 3px; border: 1px solid {border_color}; margin-bottom: 1em; min-height: 6em; overflow: hidden; text-align: right;">
    {match_html}
    </div>"""


        bracket_cols = st.columns(config.UI_CONFIG["columns_width"], gap="medium")

        for idx, stage_key in enumerate(config.STAGES):
            with bracket_cols[idx]:
                st.subheader(config.ROUND_DICT.get(stage_key, stage_key))

                stage_spacers = config.UI_CONFIG["spacers"].get(stage_key, {})
                if "top" in stage_spacers:
                    st.markdown(get_spacer_html(stage_spacers["top"]), unsafe_allow_html=True)

                if idx == 0:
                    matches_in_stage = list(config.TEAMS.keys())
                else:
                    matches_in_stage = [m for m in config.BRACKET_STRUCTURE if m.startswith(stage_key)]

                for m_id in matches_in_stage:
                    w_guess = current_display_guesses.get(m_id)
                    a_winner = actual_results.get(m_id)

                    # קריאה לפונקציה עם 7 פרמטרים בדיוק
                    st.markdown(get_match_box_html(
                        m_id,
                        w_guess,
                        eliminated_teams,
                        a_winner,
                        is_actual_view,
                        raw_user_obj,
                        config
                    ), unsafe_allow_html=True)

                    if "between" in stage_spacers:
                        st.markdown(get_spacer_html(stage_spacers["between"]), unsafe_allow_html=True)

    with tab_add:
        st.header("✍️ ניהול ניחושים")
        tournament_started = len(actual_results) > 0
        all_users = list(all_guesses.keys())

        if tournament_started:
            st.warning("הטורניר כבר התחיל! לא ניתן להוסיף משתתפים חדשים. ניתן רק לעדכן ניחושים קיימים.")
            user_name = st.selectbox("בחר משתתף לעדכון:", all_users) if all_users else None
        else:
            mode = st.radio("בחר פעולה:", ["משתתף חדש", "עדכון משתתף קיים"])
            if mode == "משתתף חדש":
                user_name = st.text_input("הכנס שם משתתף חדש:")
                if user_name in all_users: st.error("השם כבר קיים."); user_name = None
            else:
                user_name = st.selectbox("בחר משתתף לעדכון:", all_users)

        if user_name:
            st.write(f"### עריכת הניחוש של: **{user_name}**")
            user_obj = all_guesses.get(user_name, {})
            effective_guesses = logic.get_effective_guesses(user_obj, config)
            new_guesses = {}

            base_stage = config.STAGES[0]
            st.write("---")
            st.subheader(f"שלב {config.ROUND_DICT.get(base_stage, base_stage)} (נעול)")
            for m_id, participants in config.TEAMS.items():
                new_guesses[m_id] = effective_guesses.get(m_id) or participants[0]
                st.write(
                    f"**משחק {config.ROUND_DICT.get(m_id, m_id)}:** {participants[0]} - {participants[1]} | הניחוש שלך: **{new_guesses[m_id]}** (נעול)")

            eliminated_teams = logic.get_eliminated_teams(actual_results, config)

            for stage in config.STAGES[1:]:
                st.write("---")
                st.subheader(f"שלב {config.ROUND_DICT.get(stage, stage)}")
                for m_id in [m for m in config.BRACKET_STRUCTURE if m.startswith(stage)]:
                    participants = logic.get_participant_teams(m_id, new_guesses, actual_results, config)
                    if "TBD" not in participants:
                        if actual_results.get(m_id):
                            new_guesses[m_id] = effective_guesses.get(m_id) or participants[0]
                            st.write(
                                f"**משחק {config.ROUND_DICT.get(m_id, m_id)}:** {participants[0]} - {participants[1]} | הניחוש שלך (נעול): **{new_guesses[m_id]}**")
                        else:
                            idx = participants.index(effective_guesses.get(m_id)) if effective_guesses.get(
                                m_id) in participants else 0
                            new_guesses[m_id] = st.radio(f"משחק {config.ROUND_DICT.get(m_id, m_id)}: ", participants,
                                                         index=idx,
                                                         key=f"edit_{user_name}_{m_id}", format_func=lambda
                                    l: f"{l} (הודחה! ❌)" if l in eliminated_teams else l)
                            if effective_guesses.get(m_id) in eliminated_teams: st.warning(
                                "שים לב: הניחוש הקיים הוא של קבוצה שהודחה. עליך לתקן אותו.")
                    else:
                        st.info(f"משחק {config.ROUND_DICT.get(m_id, m_id)}: מחכה לתוצאות מהשלבים הקודמים...")

            if st.button("שמור עדכון ניחוש"):
                if user_name.strip() == "":
                    st.error("חובה להזין שם!")
                else:
                    # זיהוי דינמי של השלב למילון התיקונים המדויק
                    active_bucket = "base"
                    for stage in reversed(config.STAGES[:-1]):
                        if any(k.startswith(stage) for k in actual_results):
                            active_bucket = f"corrections_after_{stage}"
                            break

                    for stage in config.STAGES[:-1]:
                        b_name = f"corrections_after_{stage}"
                        if b_name not in user_obj: user_obj[b_name] = {}

                    if active_bucket == "base":
                        for m, v in new_guesses.items(): user_obj[m] = v
                    else:
                        for m, v in new_guesses.items():
                            if m.startswith(base_stage): continue
                            if effective_guesses.get(m) != v:
                                user_obj[active_bucket][m] = v

                    data_manager.save_user_guess(comp_id, user_name, user_obj)
                    st.success(f"הניחוש של {user_name} עודכן בהצלחה!")
                    st.rerun()

    with tab_admin:
        st.header("⚙️ תוצאות אמת (Admin)")
        st.write("עדכן כאן את הקבוצות שבאמת ניצחו במציאות:")
        updated_actual = actual_results.copy()
        for m_id in list(config.TEAMS.keys()) + list(config.BRACKET_STRUCTURE.keys()):
            participants = logic.get_participant_teams(m_id, {}, updated_actual, config)
            if "TBD" not in participants:
                options = ["טרם נקבע"] + participants
                current_val = updated_actual.get(m_id, "טרם נקבע")
                choice = st.selectbox(f"המנצחת האמיתית ב{config.ROUND_DICT.get(m_id, m_id)}:", options,
                                      index=options.index(current_val) if current_val in options else 0)
                if choice != "טרם נקבע": updated_actual[m_id] = choice
        if st.button("תוצאות אמת"):
            data_manager.save_actual_results(comp_id, updated_actual)
            st.success("התוצאות עודכנו! כל הניקוד חושב מחדש.")
            st.rerun()

        st.write("---")
        st.subheader("⚠️ אזור מסוכן")
        if st.button("מחק את כל הניחושים והתוצאות (Reset)"):
            data_manager.delete_all_data(comp_id)
            st.warning("כל הנתונים נמחקו. המערכת תתארס עכשיו...")
            st.rerun()


if __name__ == "__main__":
    main()