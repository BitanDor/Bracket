# app.py
import streamlit as st
import pandas as pd
import logic
import data_manager
import ui_components
from tournaments import ucl_2026_config, nba_2026_config

# רישום התחרויות הזמינות
AVAILABLE_TOURNAMENTS = {
    ucl_2026_config.ID: ucl_2026_config,
    nba_2026_config.ID: nba_2026_config
}


def main():
    st.set_page_config(page_title="Bitan's Bracket", layout="wide", page_icon="🏆")

    # --- 1. בחירת תחרות ---
    col1, _ = st.columns([1, 4])
    with col1:
        comp_id = st.selectbox("בחר תחרות:", list(AVAILABLE_TOURNAMENTS.keys()),
                               format_func=lambda x: AVAILABLE_TOURNAMENTS[x].NAME)

    config = AVAILABLE_TOURNAMENTS[comp_id]
    st.title(f"Bitan's Bracket - {config.NAME} 🏆")

    # --- 2. טעינת נתונים ---
    all_guesses = data_manager.load_all_guesses(comp_id)
    actual_results = data_manager.load_actual_results(comp_id)

    # --- 3. סיידבר: טבלת ניקוד ---
    render_sidebar(all_guesses, actual_results, config)

    # --- 4. טאבים בממשק הראשי ---
    tab_tree, tab_add, tab_admin = st.tabs(["🌳 עץ הטורניר", "✍️ ניהול ניחושים", "⚙️ תוצאות אמת"])

    with tab_tree:
        render_tree_tab(all_guesses, actual_results, config)

    with tab_add:
        render_add_tab(all_guesses, actual_results, config, comp_id)

    with tab_admin:
        render_admin_tab(actual_results, config, comp_id)


def render_sidebar(all_guesses, actual_results, config):
    st.sidebar.header("📊 טבלת ניקוד")
    leaderboard_data = []
    for user, user_obj in all_guesses.items():
        score, _ = logic.calculate_score(user_obj, actual_results, config)
        effective_guesses = logic.get_effective_guesses(user_obj, config)

        # זיהוי הזוכה (תואם ל-UCL ול-NBA)
        winner = effective_guesses.get("FINAL") or effective_guesses.get("FINALS", logic.NOT_DETERMINED)
        flag = config.TEAM_FLAGS.get(winner, "")
        winner_display = f"{flag} {winner}" if winner != logic.NOT_DETERMINED else "טרם נקבע"

        leaderboard_data.append({"שם": user, "זוכה": winner_display, "נקודות": score})

    if leaderboard_data:
        df = pd.DataFrame(leaderboard_data).sort_values(by="נקודות", ascending=False)
        df.index = range(1, len(df) + 1)
        df.index.name = "מיקום"
        st.sidebar.table(df)
    else:
        st.sidebar.write("עוד אין ניחושים.")


def render_tree_tab(all_guesses, actual_results, config):
    st.header(" 🌳 עץ הטורניר")
    view_user = st.selectbox("בחר משתתף כדי לראות את העץ שלו:", ["תוצאות אמת"] + list(all_guesses.keys()))

    is_actual_view = (view_user == "תוצאות אמת")
    raw_user_obj = {} if is_actual_view else all_guesses.get(view_user, {})
    current_display_guesses = actual_results if is_actual_view else logic.get_effective_guesses(raw_user_obj, config)

    # הפרדת שלבי פליי-אין/מוקדמות
    preliminary_stages = [s for s in config.STAGES if s.startswith("PLAY_IN")]
    main_stages = [s for s in config.STAGES if not s.startswith("PLAY_IN")]
    start_idx = len(preliminary_stages)

    # יצירת העץ המרכזי
    main_cols_width = config.UI_CONFIG["columns_width"][start_idx:]
    if len(main_cols_width) < len(main_stages):
        main_cols_width += [1.0] * (len(main_stages) - len(main_cols_width))

    bracket_cols = st.columns(main_cols_width, gap="medium")

    for idx, stage_key in enumerate(main_stages, start=start_idx):
        with bracket_cols[idx - start_idx]:
            st.subheader(config.ROUND_DICT.get(stage_key, stage_key))
            stage_spacers = config.UI_CONFIG["spacers"].get(stage_key, {})

            if "top" in stage_spacers:
                st.write(f"<div style='height: {stage_spacers['top']}em;'></div>", unsafe_allow_html=True)

            matches_in_stage = [m for m in config.BRACKET_STRUCTURE if m.startswith(stage_key)]
            # בטורניר בלי פליי-אין (כמו UCL), השלב הראשון נלקח מ-TEAMS
            if idx == 0:
                matches_in_stage = list(config.TEAMS.keys())

            for m_id in matches_in_stage:
                st.markdown(ui_components.get_match_box_html(
                    m_id,
                    current_display_guesses.get(m_id),
                    is_actual_view,
                    raw_user_obj,
                    config,
                    current_display_guesses,  # המילון שמשמש לחישוב המשתתפים
                    actual_results  # תוצאות האמת לחישוב מי עלה באמת
                ), unsafe_allow_html=True)

                if "between" in stage_spacers:
                    st.write(f"<div style='height: {stage_spacers['between']}em;'></div>", unsafe_allow_html=True)

    # הצגת פליי-אין למטה בנפרד
    if preliminary_stages:
        st.write("---")
        st.header(f"🏀 משחקי ה-Play-In")
        all_pi = list(config.TEAMS.keys()) + [m for m in config.BRACKET_STRUCTURE if m.startswith("PLAY_IN")]
        pi_cols = st.columns(len(all_pi))
        for i, m_id in enumerate(all_pi):
            with pi_cols[i]:
                st.caption(config.ROUND_DICT.get(m_id, m_id))
                st.markdown(ui_components.get_match_box_html(
                    m_id, current_display_guesses.get(m_id), is_actual_view,
                    raw_user_obj, config, current_display_guesses, actual_results
                ), unsafe_allow_html=True)


def render_add_tab(all_guesses, actual_results, config, comp_id):
    st.header("✍️ ניהול ניחושים")
    tournament_started = len(actual_results) > 0
    all_users = list(all_guesses.keys())

    if tournament_started:
        st.warning("הטורניר כבר התחיל! ניתן רק לעדכן ניחושים קיימים.")
        user_name = st.selectbox("בחר משתתף:", all_users) if all_users else None
    else:
        mode = st.radio("פעולה:", ["חדש", "עדכון"], horizontal=True)
        user_name = st.text_input("שם משתתף:") if mode == "חדש" else st.selectbox("בחר:", all_users)

    if user_name:
        user_obj = all_guesses.get(user_name, {})
        effective_guesses = logic.get_effective_guesses(user_obj, config)
        new_guesses = {}

        for idx, stage in enumerate(config.STAGES):
            st.write("---")
            st.subheader(config.ROUND_DICT.get(stage, stage))

            stage_matches = list(config.TEAMS.keys()) if idx == 0 else [m for m in config.BRACKET_STRUCTURE if
                                                                        m.startswith(stage)]

            for m_id in stage_matches:
                participants = logic.get_participant_teams(m_id, new_guesses, actual_results, config)

                if logic.NOT_DETERMINED not in participants:
                    current_guess = effective_guesses.get(m_id)
                    actual_winner = actual_results.get(m_id)

                    # 1. טיפול במשחק סגור (עם תוצאת אמת)
                    if actual_winner and actual_winner != logic.NOT_DETERMINED:
                        new_guesses[m_id] = current_guess or actual_winner
                        # הצגת תוצאת האמת והניחוש המקורי (בסוגריים)
                        guess_info = f" (הניחוש שלך: {current_guess})" if current_guess else ""
                        st.write(
                            f"**{config.ROUND_DICT.get(m_id, m_id)}:** תוצאת אמת: **{actual_winner}**{guess_info} 🔒")

                    else:
                        # 2. טיפול במשחק עתידי - בדיקת היתכנות הניחוש
                        if current_guess and current_guess != logic.NOT_DETERMINED and current_guess not in participants:
                            st.error(
                                f"⚠️ **ניחוש דורש תיקון:** ניחשת ש-**{current_guess}** תנצח, אך לפי תוצאות האמת/הניחושים הקודמים, המשחק הוא בין **{participants[0]}** ל-**{participants[1]}**.")

                        # רדיו לבחירת המנצחת
                        default_idx = participants.index(current_guess) if current_guess in participants else 0
                        new_guesses[m_id] = st.radio(f"מנצחת - {config.ROUND_DICT.get(m_id, m_id)}:",
                                                     participants, index=default_idx, key=f"r_{user_name}_{m_id}")
                else:
                    st.info(f"{config.ROUND_DICT.get(m_id, m_id)}: מחכה לתוצאות מהשלבים הקודמים...")

        if st.button("שמור ניחוש"):
            active_bucket = "base"
            for s in reversed(config.STAGES[:-1]):
                if any(k.startswith(s) for k in actual_results):
                    active_bucket = f"corrections_after_{s}"
                    break

            for m, v in new_guesses.items():
                # לוגיקה אחידה לכל המשחקים:
                # אם הטורניר לא התחיל, שומרים ב-BASE.
                # אם התחיל, שומרים בבאקט הפעיל רק אם יש שינוי.
                if active_bucket == "base":
                    user_obj[m] = v
                else:
                    if effective_guesses.get(m) != v:
                        bucket_key = f"active_bucket_{active_bucket}"  # למניעת התנגשות שמות
                        if active_bucket not in user_obj: user_obj[active_bucket] = {}
                        user_obj[active_bucket][m] = v

            data_manager.save_user_guess(comp_id, user_name, user_obj)
            st.success("נשמר!")
            st.rerun()


def render_admin_tab(actual_results, config, comp_id):
    st.header("⚙️ תוצאות אמת (Admin)")
    updated_actual = actual_results.copy()
    all_possible_matches = list(config.TEAMS.keys()) + list(config.BRACKET_STRUCTURE.keys())

    for m_id in all_possible_matches:
        participants = logic.get_participant_teams(m_id, {}, updated_actual, config)
        if logic.NOT_DETERMINED not in participants:
            # תצוגה בעברית אבל ערך לוגי באנגלית
            options = [logic.NOT_DETERMINED] + participants
            current = updated_actual.get(m_id, logic.NOT_DETERMINED)

            # format_func דואג שהמשתמש יראה עברית, אבל הקוד יקבל "TBD"
            choice = st.selectbox(f"מנצחת ב-{config.ROUND_DICT.get(m_id, m_id)}:",
                                  options,
                                  index=options.index(current) if current in options else 0,
                                  format_func=lambda x: "טרם נקבע" if x == logic.NOT_DETERMINED else x)

            updated_actual[m_id] = choice


if __name__ == "__main__":
    main()