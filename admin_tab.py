import secrets
import streamlit as st
import logic
import data_manager
import ai_commentary

def render_admin_tab(actual_results, config, comp_id):
    st.header("⚙️ ניהול (Admin)")
    updated_actual = actual_results.copy()
    all_possible_matches = list(config.TEAMS.keys()) + list(config.BRACKET_STRUCTURE.keys())

    for m_id in all_possible_matches:
        participants = logic.get_participant_teams(m_id, {}, updated_actual, config)
        if logic.NOT_DETERMINED not in participants:
            options = [logic.NOT_DETERMINED] + participants
            current = updated_actual.get(m_id, logic.NOT_DETERMINED)
            choice = st.selectbox(f"מנצחת ב-{config.ROUND_DICT.get(m_id, m_id)}:", options,
                                  index=options.index(current) if current in options else 0,
                                  format_func=lambda x: "טרם נקבע" if x == logic.NOT_DETERMINED else x)
            updated_actual[m_id] = choice

    if st.button("עדכן תוצאות"):
        data_manager.save_actual_results(comp_id, updated_actual)
        with st.spinner("Gemini מנתח את התוצאות ומכין פרשנות..."):
            # טעינת נתונים טריים לצורך הפרשנות
            all_guesses = data_manager.load_all_guesses(comp_id)
            ai_commentary.update_tournament_commentary(comp_id, config, all_guesses, updated_actual)

        st.success("התוצאות והפרשנות עודכנו!")
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