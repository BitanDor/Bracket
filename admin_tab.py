# admin_tab.py
import secrets
import streamlit as st
import logic
import data_manager
import ai_commentary


def render_admin_tab(actual_results, config, comp_id, uid_to_name):
    st.header("⚙️ ניהול (Admin)")

    # עבודה על עותק כדי למנוע שינויים לא רצויים לפני לחיצה על "שמור"
    updated_actual = actual_results.copy()
    all_possible_matches = list(config.TEAMS.keys()) + list(config.BRACKET_STRUCTURE.keys())

    # בדיקה האם הטורניר תומך בתוצאה מדויקת (מכפיל פי 3)
    exact_enabled = getattr(config, "IS_EXACT_ENABLED", False)

    st.subheader("🏆 עדכון תוצאות אמת")
    for m_id in all_possible_matches:
        # שליפת המשתתפים האמיתיים למשחק זה (רקורסיבית)
        participants = logic.get_participant_teams(m_id, {}, updated_actual, config)

        if logic.NOT_DETERMINED not in participants:
            # שליפת המצב הקיים מה-JSON תוך שימוש בנרמול
            raw_current = updated_actual.get(m_id, logic.NOT_DETERMINED)
            current_winner = logic.get_winner_name(raw_current)
            current_score = logic.get_winner_result(raw_current)

            col1, col2 = st.columns([2, 1])

            with col1:
                options = [logic.NOT_DETERMINED] + participants
                choice = st.selectbox(
                    f"מנצחת ב-{config.ROUND_DICT.get(m_id, m_id)}:",
                    options,
                    index=options.index(current_winner) if current_winner in options else 0,
                    format_func=lambda x: "טרם נקבע" if x == logic.NOT_DETERMINED else x,
                    key=f"admin_win_{m_id}"
                )

            with col2:
                # הזנת תוצאה מדויקת (רק ב-NBA)
                if exact_enabled and choice != logic.NOT_DETERMINED:
                    exact_options = getattr(config, "EXACT_OPTIONS", [4, 5, 6, 7])
                    score_choice = st.radio(
                        f"מספר משחקים:",
                        exact_options,
                        index=exact_options.index(current_score) if current_score in exact_options else 0,
                        horizontal=True,
                        key=f"admin_score_{m_id}"
                    )
                    # שמירה כמערך [winner, score]
                    updated_actual[m_id] = [choice, score_choice]
                else:
                    updated_actual[m_id] = choice

    if st.button("💾 שמור תוצאות אמת", use_container_width=True):
        previous_actual = actual_results.copy()
        data_manager.save_actual_results(comp_id, updated_actual)

        # עדכון הפרשנות ב-AI מיד לאחר עדכון התוצאות
        with st.spinner("🎙️ הפרשן מנתח את הטבלה..."):
            all_guesses = data_manager.load_all_guesses(comp_id)
            success = ai_commentary.update_tournament_commentary(
                comp_id,
                config,
                all_guesses,
                previous_actual,
                updated_actual,
                uid_to_name,
            )

        if success:
            st.success("התוצאות והפרשנות עודכנו בהצלחה!")
        else:
            st.warning("התוצאות עודכנו, אך הפרשן לא הצליח להגיב. נסה שוב בעדכון הבא.")
        st.rerun()

    # --- Secure Reset Section ---
    st.write("---")
    st.subheader("⚠️ DANGER ZONE")

    if 'reset_code' not in st.session_state:
        st.session_state.reset_code = str(secrets.randbelow(9000) + 1000)

    confirm_code = st.session_state.reset_code
    st.error(f"פעולה זו תמחק לצמיתות את כל הניחושים ותוצאות האמת של טורניר {config.NAME}.")
    st.write(f"כדי לאשר, הקלד את הקוד **{confirm_code}** ולחץ על הכפתור למטה.")

    user_input = st.text_input("הכנס קוד איפוס:", key="admin_reset_input")
    reset_disabled = (user_input != confirm_code)

    if st.button("🔥 איפוס כל הנתונים", type="primary", use_container_width=True, disabled=reset_disabled):
        data_manager.delete_all_data(comp_id)
        del st.session_state.reset_code
        st.success("הנתונים אופסו בהצלחה.")
        st.rerun()