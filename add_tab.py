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

        # אתחול עם הניחושים הקיימים (כאן הלוגיקה תשתמש ב-get_winner_name בתוך logic)
        new_guesses = effective_guesses.copy()

        # בדיקה האם הטורניר תומך בתוצאה מדויקת
        exact_enabled = getattr(config, "IS_EXACT_ENABLED", False)

        for idx, stage in enumerate(config.STAGES):
            st.write("---")
            st.subheader(config.ROUND_DICT.get(stage, stage))

            stage_matches = list(config.TEAMS.keys()) if idx == 0 else [m for m in config.BRACKET_STRUCTURE if
                                                                        m.startswith(stage)]

            for m_id in stage_matches:
                actual_val_raw = actual_results.get(m_id)
                actual_winner = logic.get_winner_name(actual_val_raw)

                guess_val_raw = effective_guesses.get(m_id)
                current_guess_winner = logic.get_winner_name(guess_val_raw)
                current_guess_score = logic.get_winner_result(guess_val_raw)

                # 1. בדיקה האם המשחק כבר הוכרע
                if actual_winner and actual_winner != logic.NOT_DETERMINED:
                    new_guesses[m_id] = guess_val_raw or actual_val_raw

                    # הצגת פרטי הניחוש (כולל תוצאה אם יש)
                    score_str = f" ({current_guess_score} משחקים)" if current_guess_score else ""
                    guess_info = f" (ניחוש שלך: {current_guess_winner}{score_str})" if current_guess_winner else ""

                    actual_score = logic.get_winner_result(actual_val_raw)
                    actual_score_str = f" [{actual_score}]" if actual_score else ""

                    st.write(
                        f"**{config.ROUND_DICT.get(m_id, m_id)}:** תוצאת אמת: **{actual_winner}**{actual_score_str}{guess_info} 🔒")
                    continue

                # 2. חישוב משתתפים (מבוסס על שמות בלבד הודות ל-logic המעודכן)
                participants = logic.get_participant_teams(m_id, new_guesses, actual_results, config)

                if logic.NOT_DETERMINED not in participants:
                    # אזהרה על ניחוש לא אפשרי
                    if current_guess_winner and current_guess_winner != logic.NOT_DETERMINED and current_guess_winner not in participants:
                        st.error(
                            f"⚠️ **Fix required:** You guessed **{current_guess_winner}** wins, but the game is between **{participants[0]}** and **{participants[1]}**.")

                    # בחירת מנצחת
                    default_idx = participants.index(
                        current_guess_winner) if current_guess_winner in participants else 0
                    chosen_winner = st.radio(f"מנצחת - {config.ROUND_DICT.get(m_id, m_id)}:",
                                             participants, index=default_idx, key=f"r_win_{user_name}_{m_id}")

                    # בחירת תוצאה מדויקת (רק אם רלוונטי)
                    if exact_enabled:
                        exact_opts = getattr(config, "EXACT_OPTIONS", [4, 5, 6, 7])
                        chosen_score = st.radio(f"בכמה משחקים? ({chosen_winner})",
                                                exact_opts,
                                                index=exact_opts.index(
                                                    current_guess_score) if current_guess_score in exact_opts else 0,
                                                horizontal=True,
                                                key=f"r_score_{user_name}_{m_id}")
                        new_guesses[m_id] = [chosen_winner, chosen_score]
                    else:
                        new_guesses[m_id] = chosen_winner
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