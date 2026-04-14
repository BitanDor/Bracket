import secrets
import streamlit as st
import logic
import data_manager
import ai_commentary


def render_admin_tab(actual_results, config, comp_id):
    st.header("⚙️ ניהול (Admin)")
    updated_actual = actual_results.copy()
    all_possible_matches = list(config.TEAMS.keys()) + list(config.BRACKET_STRUCTURE.keys())

    # בדיקה האם הטורניר תומך בתוצאה מדויקת
    exact_enabled = getattr(config, "IS_EXACT_ENABLED", False)

    for m_id in all_possible_matches:
        participants = logic.get_participant_teams(m_id, {}, updated_actual, config)

        if logic.NOT_DETERMINED not in participants:
            # שימוש בשכבת הנרמול כדי לשלוף את המצב הקיים מה-JSON
            raw_current = updated_actual.get(m_id, logic.NOT_DETERMINED)
            current_winner = logic.get_winner_name(raw_current)
            current_score = logic.get_winner_result(raw_current)

            # 1. בחירת מנצחת
            options = [logic.NOT_DETERMINED] + participants
            choice = st.selectbox(
                f"מנצחת ב-{config.ROUND_DICT.get(m_id, m_id)}:",
                options,
                index=options.index(current_winner) if current_winner in options else 0,
                format_func=lambda x: "טרם נקבע" if x == logic.NOT_DETERMINED else x,
                key=f"admin_win_{m_id}"
            )

            # 2. בחירת תוצאה (רק אם נבחרה מנצחת ואופציית Exact פעילה)
            if exact_enabled and choice != logic.NOT_DETERMINED:
                exact_options = getattr(config, "EXACT_OPTIONS", [4, 5, 6, 7])
                # שימוש ב-st.radio אופקי כדי לחסוך מקום
                score_choice = st.radio(
                    f"תוצאת סדרה ({choice}):",
                    exact_options,
                    index=exact_options.index(current_score) if current_score in exact_options else 0,
                    horizontal=True,
                    key=f"admin_score_{m_id}"
                )
                # שמירה כמערך: [שם קבוצה, תוצאה]
                updated_actual[m_id] = [choice, score_choice]
            else:
                # שמירה רגילה (עבור UCL או אם טרם נקבעה מנצחת)
                updated_actual[m_id] = choice

    if st.button("עדכן תוצאות"):
        data_manager.save_actual_results(comp_id, updated_actual)
        with st.spinner("Gemini generates commentary..."):
            # טעינת נתונים טריים לצורך הפרשנות
            all_guesses = data_manager.load_all_guesses(comp_id)
            success = ai_commentary.update_tournament_commentary(comp_id, config, all_guesses, updated_actual)
        if success:
            st.success("התוצאות והפרשנות עודכנו בהצלחה!")
        else:
            # אם ה-AI נכשל, אנחנו לא "מלכלכים" את ההיסטוריה בהודעות זהות
            st.warning("התוצאות עודכנו, אך הפרשן כרגע לא זמין. נסה שוב בעדכון הבא.")
            st.rerun()

    # --- Secure Reset Section (English) ---
    st.write("---")
    st.subheader("⚠️ DANGER ZONE")
    st.markdown("### Reset Tournament Data")

    # Generate random code if not exists
    if 'reset_code' not in st.session_state:
        st.session_state.reset_code = str(secrets.randbelow(9000) + 1000)

    confirm_code = st.session_state.reset_code

    st.warning(f"This action will permanently delete all user guesses and actual results for **{config.NAME}**.")
    st.write(f"To confirm, please type the code **{confirm_code}** in the box below and click the button.")

    user_input = st.text_input("Enter reset code:", key="admin_reset_input")

    # The button is disabled unless the input matches the generated code
    reset_disabled = (user_input != confirm_code)

    if st.button("RESET ALL DATA", type="primary", use_container_width=True, disabled=reset_disabled):
        data_manager.delete_all_data(comp_id)
        # Clear code from session state to regenerate next time
        del st.session_state.reset_code
        st.success("Tournament data reset successfully.")
        st.rerun()