# TO EXECUTE: streamlit run app.py

import streamlit as st
import logic
import data_manager


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
        new_guesses = effective_guesses.copy()

        for idx, stage in enumerate(config.STAGES):
            st.write("---")
            st.subheader(config.ROUND_DICT.get(stage, stage))

            stage_matches = list(config.TEAMS.keys()) if idx == 0 else [m for m in config.BRACKET_STRUCTURE if
                                                                        m.startswith(stage)]

            for m_id in stage_matches:
                actual_winner = actual_results.get(m_id)
                current_guess = effective_guesses.get(m_id)

                # 1. בדיקה ראשונה: האם המשחק כבר הוכרע ע"י האדמין?
                if actual_winner and actual_winner != logic.NOT_DETERMINED:
                    new_guesses[m_id] = current_guess or actual_winner
                    guess_info = f" (Your guess: {current_guess})" if current_guess else ""
                    st.write(f"**{config.ROUND_DICT.get(m_id, m_id)}:** True result: **{actual_winner}**{guess_info} 🔒")
                    continue

                # 2. אם לא הוכרע, מחשבים מי המשתתפים לפי הניחושים של המשתמש
                participants = logic.get_participant_teams(m_id, new_guesses, actual_results, config)

                if logic.NOT_DETERMINED not in participants:
                    # בדיקת היתכנות הניחוש הקיים
                    if current_guess and current_guess != logic.NOT_DETERMINED and current_guess not in participants:
                        st.error(
                            f"⚠️ **Fix required:** You guessed**{current_guess}** wins, but the game is between **{participants[0]}**  and **{participants[1]}**.")

                    default_idx = participants.index(current_guess) if current_guess in participants else 0
                    chosen = st.radio(f"winner - {config.ROUND_DICT.get(m_id, m_id)}:",
                                      participants, index=default_idx, key=f"r_{user_name}_{m_id}")
                    new_guesses[m_id] = chosen
                else:
                    st.info(f"{config.ROUND_DICT.get(m_id, m_id)}: מחכה לניחושים מהשלבים הקודמים...")

        if st.button("שמור ניחוש"):
            active_bucket = "base"
            for s in reversed(config.STAGES[:-1]):
                if any(k.startswith(s) for k in actual_results):
                    active_bucket = f"corrections_after_{s}"
                    break

            for m, v in new_guesses.items():
                if active_bucket == "base":
                    user_obj[m] = v
                elif effective_guesses.get(m) != v:
                    if active_bucket not in user_obj: user_obj[active_bucket] = {}
                    user_obj[active_bucket][m] = v

            data_manager.save_user_guess(comp_id, user_name, user_obj)
            st.success("הניחוש עודכן בהצלחה!")
            st.rerun()