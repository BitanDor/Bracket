# app.py
import streamlit as st
import pandas as pd
from constants import TEAMS, BRACKET_STRUCTURE, APP_TITLE
import logic
import data_manager
import os

ROUND_DICT = {f"R16_M{i}": f"שמינית הגמר {i}" for i in range(1, 9)}
ROUND_DICT.update({f"QF{i}": f"רבע הגמר {i}" for i in range(1, 5)})
ROUND_DICT.update({f"SF{i}": f"חצי הגמר {i}" for i in range(1, 3)})
ROUND_DICT["QF"] = "רבע הגמר"
ROUND_DICT["SF"] = "חצי הגמר"
ROUND_DICT["FINAL"] = "גמר"


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide", page_icon="🏆")
    competition = "UEFA Champions League 2026  🏆"
    st.title(f"Bitan's Bracket - {competition}")

    all_guesses = data_manager.load_all_guesses()
    actual_results = data_manager.load_actual_results()

    # --- sidebar: טבלת ניקוד ---
    st.sidebar.header("📊 טבלת ניקוד")

    TEAM_FLAGS = {
        "Paris Saint-Germain": "🇫🇷", "Chelsea": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Galatasaray": "🇹🇷",
        "Liverpool": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Real Madrid": "🇪🇸", "Manchester City": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "Atalanta": "🇮🇹", "Bayern Munich": "🇩🇪", "Newcastle": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "Barcelona": "🇪🇸", "Atlético Madrid": "🇪🇸", "Tottenham": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "Bodø/Glimt": "🇳🇴", "Sporting CP": "🇵🇹", "Bayer Leverkusen": "🇩🇪", "Arsenal": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"
    }

    leaderboard_data = []
    for user, user_obj in all_guesses.items():
        score, _ = logic.calculate_score(user_obj, actual_results)
        effective_guesses = logic.get_effective_guesses(user_obj)

        predicted_winner = effective_guesses.get("FINAL", "TBD")
        flag = TEAM_FLAGS.get(predicted_winner, "")
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
        current_display_guesses = actual_results if is_actual_view else logic.get_effective_guesses(raw_user_obj)

        eliminated_teams = logic.get_eliminated_teams(actual_results)

        def format_team(team_name, is_winner_node):
            if team_name == "TBD": return "<i>TBD</i>"
            flag = TEAM_FLAGS.get(team_name, "")
            prefix_icon = " 🌟" if team_name == is_winner_node else ""
            style = "font-weight: bold;" if team_name == is_winner_node else ""
            return f"<span style='{style}'>{flag} {team_name}{prefix_icon}</span>"

        def get_match_box_html(m_id, winner_node, user_eliminated_node, actual_w_node):
            participants = logic.get_participant_teams(m_id, current_display_guesses, actual_results)
            team_a, team_b = participants[0], participants[1]
            match_html = f"<div style='line-height: 1.1;'><br>{format_team(team_a, winner_node)}<br><small>vs</small><br>{format_team(team_b, winner_node)}</div>"

            # בדיקת תיקון באמצעות הלוגיקה החדשה
            is_corrected = False
            if not is_actual_view:
                _, bucket = logic.get_guess_info(raw_user_obj, m_id)
                if bucket != "BASE":
                    is_corrected = True
                    original_guess = raw_user_obj.get(m_id, "???")  # מושך את ניחוש הבסיס המקורי לחלוטין
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

        bracket_cols = st.columns([0.7, 0.7, 0.7, 1], gap="medium")

        def get_spacer_html(em_height):
            return f"<div style='height: {em_height}em;'></div>"

        # עמודת שמינית
        with bracket_cols[0]:
            st.subheader("שמינית הגמר")
            for m_id in list(TEAMS.keys()):
                w_guess = current_display_guesses.get(m_id)
                a_winner = actual_results.get(m_id)
                st.markdown(get_match_box_html(m_id, w_guess, eliminated_teams, a_winner), unsafe_allow_html=True)

        # עמודת רבע
        with bracket_cols[1]:
            st.subheader("רבע הגמר")
            st.markdown(get_spacer_html(3.5), unsafe_allow_html=True)
            for m_id in [m for m in BRACKET_STRUCTURE if m.startswith("QF")]:
                w_guess = current_display_guesses.get(m_id)
                a_winner = actual_results.get(m_id)
                st.markdown(get_match_box_html(m_id, w_guess, eliminated_teams, a_winner), unsafe_allow_html=True)
                st.markdown(get_spacer_html(7), unsafe_allow_html=True)

        # עמודת חצי
        with bracket_cols[2]:
            st.subheader("חצי הגמר")
            st.markdown(get_spacer_html(10.5), unsafe_allow_html=True)
            for m_id in [m for m in BRACKET_STRUCTURE if m.startswith("SF")]:
                w_guess = current_display_guesses.get(m_id)
                a_winner = actual_results.get(m_id)
                st.markdown(get_match_box_html(m_id, w_guess, eliminated_teams, a_winner), unsafe_allow_html=True)
                st.markdown(get_spacer_html(21), unsafe_allow_html=True)

        # עמודת גמר
        with bracket_cols[3]:
            st.subheader("גמר")
            st.markdown(get_spacer_html(24), unsafe_allow_html=True)
            w_guess = current_display_guesses.get("FINAL")
            a_winner = actual_results.get("FINAL")
            st.markdown(get_match_box_html("FINAL", w_guess, eliminated_teams, a_winner), unsafe_allow_html=True)

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
            effective_guesses = logic.get_effective_guesses(user_obj)
            new_guesses = {}

            st.write("---");
            st.subheader("שלב שמינית הגמר (נעול)")
            for m_id, participants in TEAMS.items():
                new_guesses[m_id] = effective_guesses.get(m_id) or participants[0]
                st.write(
                    f"**משחק {ROUND_DICT[m_id]}:** {participants[0]} - {participants[1]} | הניחוש שלך: **{new_guesses[m_id]}** (נעול)")

            eliminated_teams = logic.get_eliminated_teams(actual_results)
            for stage in ["QF", "SF", "FINAL"]:
                st.write("---");
                st.subheader(f"שלב {ROUND_DICT.get(stage, stage)}")
                for m_id in [m for m in BRACKET_STRUCTURE if m.startswith(stage)]:
                    participants = logic.get_participant_teams(m_id, new_guesses, actual_results)
                    if "TBD" not in participants:
                        if actual_results.get(m_id):
                            new_guesses[m_id] = effective_guesses.get(m_id) or participants[0]
                            st.write(
                                f"**משחק {ROUND_DICT[m_id]}:** {participants[0]} - {participants[1]} | הניחוש שלך (נעול): **{new_guesses[m_id]}**")
                        else:
                            idx = participants.index(effective_guesses.get(m_id)) if effective_guesses.get(
                                m_id) in participants else 0
                            new_guesses[m_id] = st.radio(f"משחק {ROUND_DICT[m_id]}: ", participants, index=idx,
                                                         key=f"edit_{user_name}_{m_id}", format_func=lambda
                                    l: f"{l} (הודחה! ❌)" if l in eliminated_teams else l)
                            if effective_guesses.get(m_id) in eliminated_teams: st.warning(
                                "שים לב: הניחוש הקיים הוא של קבוצה שהודחה. עליך לתקן אותו.")
                    else:
                        st.info(f"משחק {ROUND_DICT[m_id]}: מחכה לתוצאות מהשלבים הקודמים...")

            if st.button("שמור עדכון ניחוש"):
                if user_name.strip() == "":
                    st.error("חובה להזין שם!")
                else:
                    # זיהוי השלב הנוכחי ליצירת ההיסטוריה כפי שהצעת
                    has_sf = any(k.startswith("SF") for k in actual_results)
                    has_qf = any(k.startswith("QF") for k in actual_results)
                    has_r16 = any(k.startswith("R16") for k in actual_results)

                    active_bucket = "corrections_after_SF" if has_sf else (
                        "corrections_after_QF" if has_qf else ("corrections_after_R16" if has_r16 else "base"))

                    # יצירת המבנה במידה ולא קיים
                    for b in ["corrections_after_R16", "corrections_after_QF", "corrections_after_SF"]:
                        if b not in user_obj: user_obj[b] = {}

                    if active_bucket == "base":
                        for m, v in new_guesses.items(): user_obj[m] = v
                    else:
                        # שמירת הדלתא בלבד
                        for m, v in new_guesses.items():
                            if m.startswith("R16"): continue
                            if effective_guesses.get(m) != v:
                                user_obj[active_bucket][m] = v

                    data_manager.save_user_guess(user_name, user_obj)
                    st.success(f"הניחוש של {user_name} עודכן בהצלחה!");
                    st.rerun()

    with tab_admin:
        st.header("⚙️ תוצאות אמת (Admin)")
        st.write("עדכן כאן את הקבוצות שבאמת ניצחו במציאות:")
        updated_actual = actual_results.copy()
        for m_id in list(TEAMS.keys()) + list(BRACKET_STRUCTURE.keys()):
            participants = logic.get_participant_teams(m_id, {}, updated_actual)
            if "TBD" not in participants:
                options = ["טרם נקבע"] + participants
                current_val = updated_actual.get(m_id, "טרם נקבע")
                choice = st.selectbox(f"המנצחת האמיתית ב{ROUND_DICT[m_id]}:", options,
                                      index=options.index(current_val) if current_val in options else 0)
                if choice != "טרם נקבע": updated_actual[m_id] = choice
        if st.button("תוצאות אמת"): data_manager.save_actual_results(updated_actual); st.success(
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