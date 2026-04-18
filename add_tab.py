import streamlit as st
import logic
import data_manager


def render_add_tab(all_guesses, actual_results, config, comp_id, user_id, user_role, display_name):
    st.header("✍️ ניהול ניחושים")

    uid_to_name = data_manager.get_uid_to_name_map()
    if user_role == "admin":
        uids_in_comp = list(all_guesses.keys())
        if user_id not in uids_in_comp:
            uids_in_comp.append(user_id)
        user_to_edit = st.selectbox(
            "בחר משתתף לעריכה:",
            uids_in_comp,
            index=uids_in_comp.index(user_id) if user_id in uids_in_comp else 0,
            format_func=lambda x: uid_to_name.get(x, x)  # מציג שם יפה במקום ID
        )
        st.info(f"מצב אדמין: הנך עורך את הניחושים של **{uid_to_name.get(user_to_edit, user_to_edit)}**")
    else:
        user_to_edit = user_id
        st.info(f"הנך עורך את הניחושים שלך: **{display_name}**")
    user_obj = all_guesses.get(user_to_edit, {})
    effective_guesses = logic.get_effective_guesses(user_obj, config)
    new_guesses = effective_guesses.copy()

    exact_enabled = getattr(config, "IS_EXACT_ENABLED", False)
    tournament_started = len(actual_results) > 0

    if tournament_started:
        st.warning("הטורניר כבר התחיל! שינוי ניחושים כעת ייחשב כ'תיקון' ויגרור ניקוד מופחת.")

    # --- 2. מעבר על שלבי הטורניר והצגת המשחקים ---
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

            if actual_winner and actual_winner != logic.NOT_DETERMINED:
                new_guesses[m_id] = guess_val_raw or actual_val_raw
                score_str = f" ({current_guess_score} משחקים)" if current_guess_score else ""
                guess_info = f" (ניחוש: {current_guess_winner}{score_str})" if current_guess_winner else ""
                st.write(f"**{config.ROUND_DICT.get(m_id, m_id)}:** תוצאה: **{actual_winner}** {guess_info} 🔒")
                continue

            participants = logic.get_participant_teams(m_id, new_guesses, actual_results, config)

            if logic.NOT_DETERMINED not in participants:
                if current_guess_winner and current_guess_winner != logic.NOT_DETERMINED and current_guess_winner not in participants:
                    st.error(f"⚠️ **Correction required** {current_guess_winner} does not participates in this game")

                default_idx = participants.index(current_guess_winner) if current_guess_winner in participants else 0
                chosen_winner = st.radio(f"מנצחת - {config.ROUND_DICT.get(m_id, m_id)}:",
                                         participants, index=default_idx, key=f"r_win_{user_to_edit}_{m_id}")

                if exact_enabled:
                    exact_opts = getattr(config, "EXACT_OPTIONS", [4, 5, 6, 7])
                    chosen_score = st.radio(f"בכמה משחקים? ({chosen_winner})",
                                            exact_opts,
                                            index=exact_opts.index(
                                                current_guess_score) if current_guess_score in exact_opts else 0,
                                            horizontal=True,
                                            key=f"r_score_{user_to_edit}_{m_id}")
                    new_guesses[m_id] = [chosen_winner, chosen_score]
                else:
                    new_guesses[m_id] = chosen_winner
            else:
                st.info(f"{config.ROUND_DICT.get(m_id, m_id)}: ממתין לתוצאות קודמות...")

    st.write("---")
    if st.button("💾 שמור ניחושים", use_container_width=True):
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

        data_manager.save_user_guess(comp_id, user_to_edit, user_obj)
        st.success(f"הניחושים של {uid_to_name.get(user_to_edit, user_to_edit)} נשמרו!")
        st.rerun()