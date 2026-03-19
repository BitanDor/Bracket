# app.py
import streamlit as st
import pandas as pd
from constants import TEAMS, BRACKET_STRUCTURE, APP_TITLE
import logic
import data_manager


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

        # זיהוי קבוצות שהודחו (אנחנו משתמשים ב-logic החדש)
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
                    user_guess = current_display_guesses.get(m_id, "???")
                    actual_winner = actual_results.get(m_id)

                    # בדיקת "תיקון" (עקביות)
                    is_correction = False
                    original_text = ""
                    if not is_actual_view and not m_id.startswith("R16"):
                        planned_winners = logic.get_original_planned_winner(m_id, current_display_guesses)
                        if user_guess not in planned_winners:
                            is_correction = True
                            # מנסים למצוא מי הייתה הקבוצה המקורית כדי להציג אותה
                            original_text = f" (במקור: {planned_winners})"

                    # יצירת ה-Markdown text במקום שימוש ב-<br> בתוך display_text
                    display_text = f"**{m_id}**<br>מנצחת: {user_guess}"
                    if is_correction:
                        display_text += f"<br><small style='color: #ffaa00;'>⚠️ תוקן{original_text}</small>"

                    # --- תצוגה לפי מצב המשחק (עם HTML מותאם לכל מצב) ---
                    # העדכון פותר את בעיית ה-br על ידי שימוש ב-st.markdown עבור הכל.

                    # 1. ניחוש נכון (ירוק)
                    if not is_actual_view and actual_winner and user_guess == actual_winner:
                        st.markdown(
                            f"""<div style="background-color: #2e7d32; color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px; border: 1px solid #1b5e20;">
                            ✅ {display_text}
                            </div>""", unsafe_allow_html=True
                        )

                    # 2. ניחוש שגוי (אדום)
                    elif not is_actual_view and actual_winner and user_guess != actual_winner:
                        st.markdown(
                            f"""<div style="background-color: #c62828; color: white; padding: 10px; border-radius: 5px; margin-bottom: 10px; border: 1px solid #b71c1c;">
                            ❌ {display_text}
                            </div>""", unsafe_allow_html=True
                        )

                    # 3. ניחוש שהפך לבלתי אפשרי וטרם תוקן (שחור) - נשאר אותו דבר
                    elif not is_actual_view and not actual_winner and user_guess in eliminated_teams:
                        st.markdown(
                            f"""<div style="background-color: #1a1a1a; color: white; padding: 10px; border-radius: 5px; border: 1px solid #444; margin-bottom: 10px;">
                            {display_text}<br><small>❌ הודחה - דורש תיקון</small>
                            </div>""", unsafe_allow_html=True
                        )

                    # 4. משחק פעיל / תוקן / תוצאות אמת (כחול)
                    else:
                        # אם זה תיקון, נצבע את הטקסט קצת אחרת בתוך התיבה הכחולה
                        if is_correction:
                            st.markdown(
                                f"""<div style="background-color: #1e3a8a; color: #ffaa00; padding: 10px; border-radius: 5px; border: 1px solid #3b82f6; margin-bottom: 10px;">
                                {display_text}
                                </div>""", unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f"""<div style="background-color: #1976d2; color: white; padding: 10px; border-radius: 5px; border: 1px solid #1565c0; margin-bottom: 10px;">
                                {display_text}
                                </div>""", unsafe_allow_html=True
                            )

    with tab_add:
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

        # הצגת הטופס רק אם נבחר או הוזן שם תקין
        if user_name:
            st.write(f"### עריכת הניחוש של: **{user_name}**")
            user_current_guesses = all_guesses.get(user_name, {})
            new_guesses = {}

            # --- שלב שמינית הגמר (נעול) ---
            # העדכון פותר את בעיית עריכת שמינית הגמר על ידי נעילת הבחירה.
            st.write("---")
            st.subheader("שלב שמינית הגמר")
            for m_id, participants in TEAMS.items():
                current_guess = user_current_guesses.get(m_id) or participants[0]
                new_guesses[m_id] = current_guess

                # תצוגה נקייה ללא HTML br
                st.write(f"**משחק {m_id}:** {participants[0]} - {participants[1]}")
                st.write(f"הניחוש שלך (נעול): **{current_guess}**")

            # אנחנו צריכים eliminated_teams עבור השלבים הבאים
            eliminated_teams = logic.get_eliminated_teams(actual_results)

            # --- שלבי רבע, חצי וגמר ---
            for stage in ["QF", "SF", "FINAL"]:
                st.write("---")
                st.subheader(f"שלב ה-{stage}")
                stage_matches = [m for m in BRACKET_STRUCTURE if m.startswith(stage)]

                for m_id in stage_matches:
                    # שימוש בלוגיקה (כולל התחשבות בתוצאות אמת)
                    participants = logic.get_participant_teams(m_id, new_guesses, actual_results)

                    if "TBD" not in participants:
                        actual_winner = actual_results.get(m_id)
                        default_val = user_current_guesses.get(m_id)

                        if actual_winner:
                            # המשחק הסתיים, נעל את הבחירה.
                            current_guess = user_current_guesses.get(m_id) or participants[0]
                            new_guesses[m_id] = current_guess

                            # תצוגה נקייה ללא HTML br
                            st.write(f"**משחק {m_id}:** {participants[0]} - {participants[1]}")
                            st.write(f"הניחוש שלך (נעול, המשחק הסתיים): **{current_guess}**")
                        else:
                            # המשחק טרם הסתיים, אפשר לערוך.
                            idx = participants.index(default_val) if default_val in participants else 0

                            # חיווי לניחושים בלתי אפשריים (הודחו) בתוך ה-radio labels
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
                                st.warning(
                                    f"Invalid guess! {default_val} was eliminated. Edit your guess.")
                    else:
                        st.info(f"משחק {m_id}: מחכה לתוצאות מהשלבים הקודמים כדי להציג אפשרויות...")

            if st.button("שמור עדכון ניחוש"):
                if user_name.strip() == "":
                    st.error("חובה להזין שם!")
                else:
                    data_manager.save_user_guess(user_name, new_guesses)
                    st.success(f"הניחוש של {user_name} עודכן בהצלחה!")
                    st.rerun()

    with tab_admin:
        st.header("⚙️ ניהול תוצאות אמת (Admin)")
        st.write("עדכן כאן את הקבוצות שבאמת ניצחו במציאות:")
        updated_actual = actual_results.copy()

        all_possible_matches = list(TEAMS.keys()) + list(BRACKET_STRUCTURE.keys())
        for m_id in all_possible_matches:
            participants = logic.get_participant_teams(m_id, {}, updated_actual)
            if "TBD" not in participants:
                options = ["טרם נקבע"] + participants
                current_val = updated_actual.get(m_id, "טרם נקבע")
                choice = st.selectbox(f"המנצחת האמיתית ב-{m_id}:", options,
                                      index=options.index(current_val) if current_val in options else 0)
                if choice != "טרם נקבע":
                    updated_actual[m_id] = choice

        if st.button("עדכן תוצאות אמת"):
            data_manager.save_actual_results(updated_actual)
            st.success("התוצאות עודכנו! כל הניקוד חושב מחדש.")
            st.rerun()


if __name__ == "__main__":
    main()