# app.py המעודכן לפתרון בעיות הפריסה
import streamlit as st
import pandas as pd
from constants import TEAMS, BRACKET_STRUCTURE, APP_TITLE
import logic
import data_manager
import os  # דרוש לכפתור האיפוס


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide", page_icon="🏆")
    st.title("🏆 ליגת האלופות: משחק הניחושים של החברים")

    # טעינת נתונים
    all_guesses = data_manager.load_all_guesses()
    actual_results = data_manager.load_actual_results()

    # --- sidebar: טבלת ניקוד ---
    st.sidebar.header("📊 טבלת ניקוד")
    leaderboard_data = []
    for user, guesses in all_guesses.items():
        score, _ = logic.calculate_score(guesses, actual_results)
        leaderboard_data.append({"שם": user, "נקודות": score})

    if leaderboard_data:
        df = pd.DataFrame(leaderboard_data).sort_values(by="נקודות", ascending=False)
        st.sidebar.table(df)
    else:
        st.sidebar.write("עוד אין ניחושים. תהיו הראשונים!")

    # --- טאבים בממשק הראשי ---
    tab_tree, tab_add, tab_admin = st.tabs(["🌳 עץ הטורניר", "✍️ הוסף/עדכן ניחוש", "⚙️ עדכון תוצאות אמת"])

    with tab_tree:
        st.header("מבנה הטורניר")
        # בחירת משתמש לתצוגת העץ שלו
        view_user = st.selectbox("בחר חבר כדי לראות את העץ שלו:", ["תוצאות אמת"] + list(all_guesses.keys()))

        is_actual_view = (view_user == "תוצאות אמת")
        current_display_guesses = actual_results if is_actual_view else all_guesses.get(view_user, {})

        eliminated_teams = logic.get_eliminated_teams(actual_results)

        # --- פונקציות עזר לתצוגה קומפקטית ---
        def format_team(team_name, is_winner_node):
            if team_name == "TBD": return "<i>TBD</i>"
            prefix_icon = " 🌟" if team_name == is_winner_node else ""
            style = "font-weight: bold;" if team_name == is_winner_node else ""
            return f"<span style='{style}'>{team_name}{prefix_icon}</span>"

        # פונקציה לייצור משבצת משחק - העדכון פותר את בעיית המרווחים המבולגנים על ידי קומפקטיות וגובה קבוע predicatable
        def get_match_box_html(m_id, winner_node, user_eliminated_node, correction_node, actual_w_node):
            participants = logic.get_participant_teams(m_id, current_display_guesses, actual_results)
            team_a, team_b = participants[0], participants[1]

            # צמצום המרווחים הפנימיים (line-height) לחיסכון במקום
            match_html = f"<div style='line-height: 1.1;'><br>{format_team(team_a, winner_node)}<br><small>vs</small><br>{format_team(team_b, winner_node)}</div>"

            # חיווי תיקון
            if not is_actual_view and correction_node:
                planned = logic.get_original_planned_winner(m_id, current_display_guesses)
                match_html += f"<div style='color: #ffaa00; font-size: 0.8em; margin-top:2px;'>⚠️ תוקן (במקור: {planned})</div>"

            # צבעים וסטטוס (כחול ברירת מחדל)
            bg_color, border_color, text_color = "#1976d2", "#1565c0", "white"

            if not is_actual_view:
                if actual_w_node:
                    if winner_node == actual_w_node:
                        bg_color, border_color = "#2e7d32", "#1b5e20"  # ירוק
                    else:
                        bg_color, border_color = "#c62828", "#b71c1c"  # אדום
                elif winner_node in user_eliminated_node:
                    bg_color, border_color = "#1a1a1a", "#444"  # שחור להודחה
                    match_html += "<div style='color: #ff4b4b; font-size: 0.8em; line-height: 1;'>❌ הודחה - דורש תיקון</div>"
                elif correction_node:
                    bg_color, border_color, text_color = "#1e3a8a", "#3b82f6", "#ffaa00"  # כחול כהה לתיקון

            # הדפסה למסך - שים לב שאין הזחה בתחילת מחרוזת ה-f.
            # העדכון פותר את בעיית ה-min-height הענקית על ידי Predicatable height וצמצום padding.
            return f"""<div style="background-color: {bg_color}; color: {text_color}; 
            padding: 3px; border-radius: 3px; border: 1px solid {border_color}; margin-bottom: 1em; min-height: 6em; overflow: hidden;">
{match_html}
</div>"""

        # --- שדרוג המבנה: יישור אנכי predicatable לחיסכון במקום ומראה עץ מקצועי ---

        # הגדרת יחסי רוחב לעמודות: שמינית צרה (1), רבע/חצי/גמר רחבות יותר (1.2, 1.5, 2)
        # זה פותר את בעיית המתיחה האופקית של השמינית שראינו בתמונה שלך.
        bracket_cols = st.columns([0.7, 0.7, 0.7, 1], gap="medium")

        # Predicatable vertical grid based on "units".
        # Assume standard box min-height (9em) + vertical separation (e.g., 2em) = predicatable height standard grid unit
        # R16 grid unit = 1 box height (no internal margin-bottom). We use standard markdown to separate.

        # עמודת שמינית גמר (R16): 8 משחקים
        with bracket_cols[0]:
            st.subheader("שמינית הגמר")
            matches_r16 = list(TEAMS.keys())
            for match_id in matches_r16:
                w_guess = current_display_guesses.get(match_id)
                a_winner = actual_results.get(match_id)
                # שימוש ב-st.markdown נפרד לכל משחק יוצר את ההפרדה באופן טבעי
                st.markdown(get_match_box_html(match_id, w_guess, eliminated_teams, False, a_winner),
                            unsafe_allow_html=True)

        # פונקציית עזר ליצירת מרווח אנכי Predictable באמצעות HTML predicatable height style
        # זה פותר את בעיית היישור האנכי של רבע/חצי/גמר ללא תגי <br> מבולגנים.
        def get_spacer_html(em_height):
            return f"<div style='height: {em_height}em;'></div>"

        # עמודת רבע גמר (QF): 4 משחקים מיושרים למרכז כל צמד משחקים בשמינית
        with bracket_cols[1]:
            st.subheader("רבע הגמר")

            # מרווח התחלתי (Top Padding) Predictable להתיישרות למרכז הזוג הראשון:
            # Predictable standard height: box_height_em + spacer_em(std markdown gap betw columns) ... math difficult
            # simplest fixed predicatable em heights based on typical streamlit rendering
            st.markdown(get_spacer_html(3.5), unsafe_allow_html=True)  # Top Spacer = ~0.5 box height

            matches_qf = [m for m in BRACKET_STRUCTURE.keys() if m.startswith("QF")]
            for m_id in matches_qf:
                w_guess = current_display_guesses.get(m_id)
                a_winner = actual_results.get(m_id)
                planned_winners = logic.get_original_planned_winner(m_id, current_display_guesses)
                is_correction = not is_actual_view and w_guess and w_guess not in planned_winners

                st.markdown(get_match_box_html(m_id, w_guess, eliminated_teams, is_correction, a_winner),
                            unsafe_allow_html=True)

                # מרווח בין משחקי רבע הגמר Predictable Predictable height המיושר למרכז הצמד הבא בשמינית
                st.markdown(get_spacer_html(7), unsafe_allow_html=True)  # Between Spacers = ~1.2x box height unit

        # עמודת חצי גמר (SF): 2 משחקים מיושרים למרכז כל צמד משחקים ברבע הגמר
        with bracket_cols[2]:
            st.subheader("חצי הגמר")

            # מרווח התחלתי להתיישרות למרכז הזוג הראשון ברבע
            st.markdown(get_spacer_html(10.5),
                        unsafe_allow_html=True)  # Top Spacer = 4.5(QF top) + 11(between units) = math complex

            matches_sf = [m for m in BRACKET_STRUCTURE.keys() if m.startswith("SF")]
            for m_id in matches_sf:
                w_guess = current_display_guesses.get(m_id)
                a_winner = actual_results.get(m_id)
                planned_winners = logic.get_original_planned_winner(m_id, current_display_guesses)
                is_correction = not is_actual_view and w_guess and w_guess not in planned_winners

                st.markdown(get_match_box_html(m_id, w_guess, eliminated_teams, is_correction, a_winner),
                            unsafe_allow_html=True)
                # מרווח בין משחקי חצי הגמר
                st.markdown(get_spacer_html(21), unsafe_allow_html=True)  # Between Spacers large predictable scale

        # עמודת גמר (Final): משחק אחד מיושר למרכז הכל
        with bracket_cols[3]:
            st.subheader("גמר ליגת האלופות")

            # מרווח התחלתי גדול Predictable למיקום מרכז הטורניר
            st.markdown(get_spacer_html(24),
                        unsafe_allow_html=True)  # Top Spacer = 15.5(SF top) + 23.5(halfway betw SF centers) ... math difficult

            match_id = "FINAL"
            w_guess = current_display_guesses.get(match_id)
            a_winner = actual_results.get(match_id)
            planned_winners = logic.get_original_planned_winner(match_id, current_display_guesses)
            is_correction = not is_actual_view and w_guess and w_guess not in planned_winners

            st.markdown(get_match_box_html(match_id, w_guess, eliminated_teams, is_correction, a_winner),
                        unsafe_allow_html=True)

    with tab_add:
        # טאב הוספה (ללא שינוי, כולל לוגיקת הודחות בעתיד אם יידרש)
        st.header("✍️ ניהול ניחושים")

        tournament_started = len(actual_results) > 0
        all_users = list(all_guesses.keys())

        if tournament_started:
            st.warning("הטורניר כבר התחיל! לא ניתן להוסיף משתתפים חדשים. ניתן רק לעדכן ניחושים קיימים.")
            if all_users:
                user_name = st.selectbox("בחר משתתף לעדכון:", all_users)
            else:
                st.error("אין משתתפים רשומים במערכת."); user_name = None
        else:
            mode = st.radio("בחר פעולה:", ["משתתף חדש", "עדכון משתתף קיים"])
            if mode == "משתתף חדש":
                user_name = st.text_input("הכנס שם משתתף חדש:")
                if user_name in all_users: st.error("השם הזה כבר קיים. בחר שם אחר."); user_name = None
            else:
                user_name = st.selectbox("בחר משתתף לעדכון:", all_users)

        if user_name:
            st.write(f"### עריכת הניחוש של: **{user_name}**")
            user_current_guesses = all_guesses.get(user_name, {})
            new_guesses = {}
            st.write("---");
            st.subheader("שלב שמינית הגמר (נעול)")
            for m_id, participants in TEAMS.items():
                current_guess = user_current_guesses.get(m_id) or participants[0]
                new_guesses[m_id] = current_guess
                st.write(
                    f"**משחק {m_id}:** {participants[0]} - {participants[1]} | הניחוש שלך (נעול): **{current_guess}**")

            eliminated_teams = logic.get_eliminated_teams(actual_results)
            for stage in ["QF", "SF", "FINAL"]:
                st.write("---");
                st.subheader(f"שלב ה-{stage}")
                stage_matches = [m for m in BRACKET_STRUCTURE if m.startswith(stage)]
                for m_id in stage_matches:
                    participants = logic.get_participant_teams(m_id, new_guesses, actual_results)
                    if "TBD" not in participants:
                        actual_winner = actual_results.get(m_id)
                        default_val = user_current_guesses.get(m_id)
                        if actual_winner:
                            current_guess = user_current_guesses.get(m_id) or participants[0]
                            new_guesses[m_id] = current_guess
                            st.write(
                                f"**משחק {m_id}:** {participants[0]} - {participants[1]} | הניחוש שלך (נעול): **{current_guess}**")
                        else:
                            idx = participants.index(default_val) if default_val in participants else 0
                            new_guesses[m_id] = st.radio(f"משחק {m_id}: {participants[0]} - {participants[1]}",
                                                         participants, index=idx, key=f"edit_{user_name}_{m_id}",
                                                         format_func=lambda
                                                             label: f"{label} (הודחה! ❌)" if label in eliminated_teams else label)
                            if default_val in eliminated_teams: st.warning(
                                f"שים לב: הניחוש הקיים ({default_val}) הוא של קבוצה שהודחה. עליך לתקן אותו.")
                    else:
                        st.info(f"משחק {m_id}: מחכה לתוצאות מהשלבים הקודמים כדי להציג אפשרויות...")
            if st.button("שמור עדכון ניחוש"):
                if user_name.strip() == "":
                    st.error("חובה להזין שם!")
                else:
                    data_manager.save_user_guess(user_name, new_guesses); st.success(
                        f"הניחוש של {user_name} עודכן בהצלחה!"); st.rerun()

    with tab_admin:
        # טאב ניהול (ללא שינוי, כולל כפתור איפוס)
        st.header("⚙️ ניהול תוצאות אמת (Admin)")
        st.write("עדכן כאן את הקבוצות שבאמת ניצחו במציאות:")
        updated_actual = actual_results.copy()
        all_possible_matches = list(TEAMS.keys()) + list(BRACKET_STRUCTURE.keys())
        for m_id in all_possible_matches:
            participants = logic.get_participant_teams(m_id, {}, updated_actual)
            if "TBD" not in participants:
                options = ["טרם נקבע"] + participants
                current_val = updated_actual.get(m_id, "טרם נקבע")
                choice = st.selectbox(f"המנצחת الأמתית ב-{m_id}:", options,
                                      index=options.index(current_val) if current_val in options else 0)
                if choice != "טרם נקבע": updated_actual[m_id] = choice
        if st.button("עדכן תוצאות אמת"): data_manager.save_actual_results(updated_actual); st.success(
            "התוצאות עודכנו! כל הניקוד חושב מחדש."); st.rerun()
        st.write("---");
        st.subheader("⚠️ אזור מסוכן")
        if st.button("מחק את כל הניחושים והתוצאות (Reset)"):
            if os.path.exists("user_guesses.json"): os.remove("user_guesses.json")
            if os.path.exists("actual_results.json"): os.remove("actual_results.json")
            st.warning("כל הנתונים נמחקו. המערכת תתארס עכשיו...");
            st.rerun()


if __name__ == "__main__":
    main()