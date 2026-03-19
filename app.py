# app.py
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

        # זיהוי קבוצות שהודחו
        eliminated_teams = logic.get_eliminated_teams(actual_results)

        cols = st.columns(4)
        stages = [("שמינית", "R16"), ("רבע", "QF"), ("חצי", "SF"), ("גמר", "FINAL")]

        for i, (label, prefix) in enumerate(stages):
            with cols[i]:
                st.subheader(label)
                # שליפת המשחקים הרלוונטיים לשלב הזה
                matches = [m for m in BRACKET_STRUCTURE.keys() if
                           m.startswith(prefix)] if prefix != "R16" else TEAMS.keys()

                for m_id in matches:
                    # 1. מי משחק? (לפי בחירת המשתמש או תוצאות אמת)
                    participants = logic.get_participant_teams(m_id, current_display_guesses, actual_results)
                    team_a, team_b = participants[0], participants[1]

                    # 2. מי המנצחת (הניחוש או האמת)?
                    winner_guess = current_display_guesses.get(m_id)
                    actual_winner = actual_results.get(m_id)

                    # 3. בניית תצוגת הקבוצות (הדגשת המנצחת)
                    def format_team(team_name, is_winner_node):
                        if team_name == "TBD": return "<i>TBD</i>"
                        prefix_icon = "🏆 " if team_name == is_winner_node else ""
                        style = "font-weight: bold; text-decoration: underline;" if team_name == is_winner_node else ""
                        return f"<span style='{style}'>{prefix_icon}{team_name}</span>"

                    # הקבוצה המודגשת היא המנצחת האמיתית (בתצוגת אמת) או הניחוש (בתצוגת משתמש)
                    highlight_winner = actual_winner if is_actual_view else winner_guess

                    # בניית ה-HTML של המשחק (ללא הזחה מפורשת)
                    match_html = f"<div style='line-height: 1.6;'><small>{m_id}</small><br>{format_team(team_a, highlight_winner)}<br><small>vs</small><br>{format_team(team_b, highlight_winner)}</div>"

                    # 4. קביעת צבע וסטטוס (תיקון/הדחה)
                    is_correction = False
                    if not is_actual_view and not m_id.startswith("R16"):
                        planned = logic.get_original_planned_winner(m_id, current_display_guesses)
                        if winner_guess and winner_guess not in planned:
                            is_correction = True
                            match_html += f"<div style='color: #ffaa00; font-size: 0.8em; margin-top:5px;'>⚠️ תוקן (במקור: {planned})</div>"

                    # צבעים ברירת מחדל
                    bg_color = "#1976d2"  # כחול ברירת מחדל
                    border_color = "#1565c0"
                    text_color = "white"

                    # לוגיקה מותאמת לתצוגת משתמש (העדכון פותר את הבעיה שבתמונות)
                    if not is_actual_view:
                        if actual_winner:
                            if winner_guess == actual_winner:
                                bg_color, border_color = "#2e7d32", "#1b5e20"  # ירוק לניחוש נכון
                            else:
                                bg_color, border_color = "#c62828", "#b71c1c"  # אדום לניחוש שגוי
                        elif winner_guess in eliminated_teams:
                            bg_color, border_color = "#1a1a1a", "#444"  # שחור להודחה
                            match_html += "<div style='color: #ff4b4b; font-size: 0.8em;'>❌ הודחה - דורש תיקון</div>"
                        elif is_correction:
                            bg_color, border_color, text_color = "#1e3a8a", "#3b82f6", "#ffaa00"  # כחול כהה לתיקון

                    # הדפסה למסך - שים לב שאין הזחה בתחילת מחרוזת ה-f
                    st.markdown(
                        f"""<div style="background-color: {bg_color}; color: {text_color}; padding: 12px; border-radius: 8px; border: 2px solid {border_color}; margin-bottom: 15px; min-height: 110px;">
{match_html}
</div>""", unsafe_allow_html=True
                    )

    with tab_add:
        # טאב הוספה (ללא שינוי, לתיקון בעתיד אם יידרש)
        st.header("✍️ ניהול ניחושים")

        # בדיקה אם הטורניר כבר התחיל (האם קיימות תוצאות אמת)
        tournament_started = len(actual_results) > 0
        all_users = list(all_guesses.keys())

        if tournament_started:
            st.warning("הטורניר כבר התחיל! לא ניתן להוסיף משתתפים חדשים. ניתן רק לעדכן ניחושים קיימים.")
            if all_users:
                user_name = st.selectbox("בחר משתתף לעדכון:", all_users)
            else:
                st.error("אין משתתפים רשומים במערכת.")
                user_name = None
        else:
            # הטורניר טרם התחיל - ניתן להוסיף חדשים או לעדכן קיימים
            mode = st.radio("בחר פעולה:", ["משתתף חדש", "עדכון משתתף קיים"])
            if mode == "משתתף חדש":
                user_name = st.text_input("הכנס שם משתתף חדש:")
                if user_name in all_users:
                    st.error("השם הזה כבר קיים. בחר שם אחר או עבור ל'עדכון משתתף קיים'.")
                    user_name = None
            else:
                user_name = st.selectbox("בחר משתתף לעדכון:", all_users)

        if user_name:
            st.write(f"### עריכת הניחוש של: **{user_name}**")
            user_current_guesses = all_guesses.get(user_name, {})
            new_guesses = {}

            # --- שלב שמינית הגמר (נעול) ---
            st.write("---")
            st.subheader("שלב שמינית הגמר")
            for m_id, participants in TEAMS.items():
                current_guess = user_current_guesses.get(m_id) or participants[0]
                new_guesses[m_id] = current_guess
                st.write(
                    f"**משחק {m_id}:** {participants[0]} - {participants[1]} | הניחוש שלך (נעול): **{current_guess}**")

            eliminated_teams = logic.get_eliminated_teams(actual_results)

            # --- שלבי רבע, חצי וגמר ---
            for stage in ["QF", "SF", "FINAL"]:
                st.write("---")
                st.subheader(f"שלב ה-{stage}")
                stage_matches = [m for m in BRACKET_STRUCTURE if m.startswith(stage)]

                for m_id in stage_matches:
                    participants = logic.get_participant_teams(m_id, new_guesses, actual_results)

                    if "TBD" not in participants:
                        actual_winner = actual_results.get(m_id)
                        default_val = user_current_guesses.get(m_id)

                        if actual_winner:
                            # המשחק הסתיים, נעל את הבחירה.
                            current_guess = user_current_guesses.get(m_id) or participants[0]
                            new_guesses[m_id] = current_guess
                            st.write(
                                f"**משחק {m_id}:** {participants[0]} - {participants[1]} | הניחוש שלך (נעול): **{current_guess}**")
                        else:
                            # המשחק טרם הסתיים, אפשר לערוך.
                            idx = participants.index(default_val) if default_val in participants else 0

                            # חיווי לניחושים בלתי אפשריים (הודחו)
                            def format_radio_label(label):
                                if label in eliminated_teams:
                                    return f"{label} (הודחה! ❌)"
                                return label

                            new_guesses[m_id] = st.radio(
                                f"משחק {m_id}: {participants[0]} - {participants[1]}",
                                participants,
                                index=idx,
                                key=f"edit_{user_name}_{m_id}",
                                format_func=format_radio_label
                            )

                            if default_val in eliminated_teams:
                                st.warning(f"שים לב: הניחוש הקיים ({default_val}) הוא של קבוצה שהודחה. עליך לתקן אותו.")
                    else:
                        st.info(f"משחק {m_id}: מחכה לתוצאות...")

            if st.button("שמור עדכון ניחוש"):
                if user_name.strip() == "":
                    st.error("חובה להזין שם!")
                else:
                    data_manager.save_user_guess(user_name, new_guesses)
                    st.success(f"הניחוש של {user_name} עודכן בהצלחה!")
                    st.rerun()

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
                if choice != "טרם נקבע":
                    updated_actual[m_id] = choice

        if st.button("עדכן תוצאות אמת"):
            data_manager.save_actual_results(updated_actual)
            st.success("התוצאות עודכנו! כל הניקוד חושב מחדש.")
            st.rerun()

        st.write("---")
        st.subheader("⚠️ אזור מסוכן")
        if st.button("מחק את כל הניחושים והתוצאות (Reset)"):
            if os.path.exists("user_guesses.json"):
                os.remove("user_guesses.json")
            if os.path.exists("actual_results.json"):
                os.remove("actual_results.json")
            st.warning("כל הנתונים נמחקו. המערכת תתארס עכשיו...")
            st.rerun()


if __name__ == "__main__":
    main()