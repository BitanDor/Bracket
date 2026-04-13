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
        view_user = st.selectbox("בחר משתתף כדי לראות את העץ שלו:", ["תוצאות אמת"] + list(all_guesses.keys()))

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

        # --- בדיקה האם יש שלב פליי-אין להפרדה ---
        has_play_in = config.STAGES[0] == "PLAY_IN"

        # קביעת השלבים שיוצגו בעץ המרכזי
        if has_play_in:
            main_stages = config.STAGES[1:]
            start_idx = 1
        else:
            main_stages = config.STAGES
            start_idx = 0

        main_cols_width = config.UI_CONFIG["columns_width"][start_idx:]
        bracket_cols = st.columns(main_cols_width, gap="medium")

        # --- חלק א': עץ הטורניר המרכזי ---
        for idx, stage_key in enumerate(main_stages, start=start_idx):
            with bracket_cols[idx - start_idx]:
                st.subheader(config.ROUND_DICT.get(stage_key, stage_key))

                stage_spacers = config.UI_CONFIG["spacers"].get(stage_key, {})
                if "top" in stage_spacers:
                    st.markdown(get_spacer_html(stage_spacers["top"]), unsafe_allow_html=True)

                # החלטה מאיפה למשוך את המשחקים (TEAMS לשלב הראשון בעץ, BRACKET לשאר)
                if idx == 0:
                    matches_in_stage = list(config.TEAMS.keys())
                else:
                    matches_in_stage = [m for m in config.BRACKET_STRUCTURE if m.startswith(stage_key)]

                for m_id in matches_in_stage:
                    w_guess = current_display_guesses.get(m_id)
                    a_winner = actual_results.get(m_id)

                    st.markdown(get_match_box_html(
                        m_id, w_guess, eliminated_teams, a_winner,
                        is_actual_view, raw_user_obj, config
                    ), unsafe_allow_html=True)

                    if "between" in stage_spacers:
                        st.markdown(get_spacer_html(stage_spacers["between"]), unsafe_allow_html=True)

        # --- חלק ב': אזור ה-Play-In (יוצג רק אם קיים ורק למטה) ---
        if has_play_in:
            st.write("---")
            st.header(f"🏀 משחקי ה-{config.ROUND_DICT.get('PLAY_IN', 'Play-In')}")

            play_in_matches = list(config.TEAMS.keys())
            play_in_finals = [m for m in config.BRACKET_STRUCTURE if m.startswith("PLAY_IN")]
            all_play_in = play_in_matches + play_in_finals

            pi_cols = st.columns(len(all_play_in))
            for pi_idx, m_id in enumerate(all_play_in):
                with pi_cols[pi_idx]:
                    w_guess = current_display_guesses.get(m_id)
                    a_winner = actual_results.get(m_id)
                    st.caption(config.ROUND_DICT.get(m_id, m_id))
                    st.markdown(get_match_box_html(
                        m_id, w_guess, eliminated_teams, a_winner,
                        is_actual_view, raw_user_obj, config
                    ), unsafe_allow_html=True)

        # --- הפרדה ויזואלית ---
        st.write("---")

    with tab_add:
        st.header("✍️ ניהול ניחושים")
        tournament_started = len(actual_results) > 0
        all_users = list(all_guesses.keys())

        if tournament_started:
            st.warning("הטורניר כבר התחיל! לא ניתן להוסיף משתתפים חדשים. ניתן רק לעדכן ניחושים קיימים.")
            user_name = st.selectbox("בחר משתתף לעדכון:", all_users, key="user_select_update") if all_users else None
        else:
            mode = st.radio("בחר פעולה:", ["משתתף חדש", "עדכון משתתף קיים"], key="mode_radio")
            if mode == "משתתף חדש":
                user_name = st.text_input("הכנס שם משתתף חדש:", key="new_user_input")
                if user_name in all_users:
                    st.error("השם כבר קיים.")
                    user_name = None
            else:
                user_name = st.selectbox("בחר משתתף לעדכון:", all_users, key="user_select_edit")

        if user_name:
            st.write(f"### עריכת הניחוש של: **{user_name}**")
            user_obj = all_guesses.get(user_name, {})
            # טעינת הניחושים התקפים כרגע כבסיס לעריכה
            effective_guesses = logic.get_effective_guesses(user_obj, config)
            new_guesses = {}

            eliminated_teams = logic.get_eliminated_teams(actual_results, config)

            # מעבר על כל השלבים בטורניר לפי הסדר
            for idx, stage in enumerate(config.STAGES):
                st.write("---")
                st.subheader(f"שלב {config.ROUND_DICT.get(stage, stage)}")

                # מציאת כל המשחקים השייכים לשלב הזה
                if idx == 0:
                    # בשלב הראשון לוקחים את המשחקים מ-TEAMS
                    stage_matches = list(config.TEAMS.keys())
                else:
                    # בשלבים הבאים לוקחים מתוך ה-BRACKET_STRUCTURE
                    stage_matches = [m for m in config.BRACKET_STRUCTURE if m.startswith(stage)]

                # ב-NBA, משחקי הפליי-אין על סיד 8 נמצאים ב-BRACKET (כי הם תלויים במשחקים קודמים)
                # אז אם אנחנו בשלב הפליי-אין, נוסיף גם אותם
                if stage == "PLAY_IN" and idx == 0:
                    stage_matches += [m for m in config.BRACKET_STRUCTURE if m.startswith("PLAY_IN")]

                for m_id in stage_matches:
                    participants = logic.get_participant_teams(m_id, new_guesses, actual_results, config)

                    # הצגת המשחק רק אם יש משתתפים (לא TBD)
                    if "TBD" not in participants:
                        actual_winner = actual_results.get(m_id)
                        current_guess = effective_guesses.get(m_id)

                        # אם יש תוצאת אמת - השדה נעול
                        if actual_winner:
                            new_guesses[m_id] = current_guess if current_guess else actual_winner
                            st.write(
                                f"**{config.ROUND_DICT.get(m_id, m_id)}:** {participants[0]} vs {participants[1]} | תוצאת אמת: **{actual_winner}** (נעול)")
                        else:
                            # בחירת מנצחת - כאן התיקון! השתמשנו ב-st.radio במקום st.write
                            default_idx = participants.index(current_guess) if current_guess in participants else 0

                            label = config.ROUND_DICT.get(m_id, f"משחק {m_id}")
                            new_guesses[m_id] = st.radio(
                                f"בחרו מנצחת - {label}:",
                                participants,
                                index=default_idx,
                                key=f"radio_{user_name}_{m_id}",
                                format_func=lambda l: f"{l} (הודחה! ❌)" if l in eliminated_teams else l
                            )

                            if current_guess in eliminated_teams:
                                st.warning(
                                    f"שים לב: הקבוצה שבחרת ({current_guess}) הודחה מהטורניר במציאות. עליך לתקן את הניחוש.")
                    else:
                        st.info(f"**{config.ROUND_DICT.get(m_id, m_id)}:** מחכה לתוצאות מהשלבים הקודמים...")

            if st.button("שמור עדכון ניחוש", key="save_guesses_btn"):
                if user_name.strip() == "":
                    st.error("חובה להזין שם!")
                else:
                    # לוגיקת ה-Buckets (תיקונים)
                    active_bucket = "base"
                    for stage in reversed(config.STAGES[:-1]):
                        if any(k.startswith(stage) for k in actual_results):
                            active_bucket = f"corrections_after_{stage}"
                            break

                    # יצירת מילוני התיקונים אם אינם קיימים
                    for stage in config.STAGES[:-1]:
                        b_name = f"corrections_after_{stage}"
                        if b_name not in user_obj: user_obj[b_name] = {}

                    if active_bucket == "base":
                        # בשלב הבסיס פשוט דורסים את הערכים בשורש האובייקט
                        for m, v in new_guesses.items():
                            user_obj[m] = v
                    else:
                        # אם הטורניר התחיל, שומרים רק שינויים בתוך ה-Bucket המתאים
                        for m, v in new_guesses.items():
                            # שלב הבסיס המוחלט (למשל פליי-אין) תמיד נעול לתיקונים לאחר שהתחיל
                            if m in config.TEAMS: continue

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