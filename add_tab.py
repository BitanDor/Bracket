import streamlit as st
import logic
import data_manager


def render_add_tab(all_guesses, actual_results, config, comp_id, current_user, user_role):
    st.header("✍️ ניהול ניחושים")

    # --- 1. זיהוי המשתמש לעריכה ---
    # אדמין יכול לערוך את כולם, משתמש רגיל רק את עצמו
    if user_role == "admin":
        user_list = list(all_guesses.keys())
        # אם האדמין לא ברשימת המנחשים, נוסיף אותו זמנית לבחירה
        if current_user not in user_list: user_list.append(current_user)

        user_to_edit = st.selectbox("בחר משתתף לעריכה:", user_list,
                                    index=user_list.index(current_user) if current_user in user_list else 0)
    else:
        user_to_edit = current_user
        st.info(f"הנך עורך את הניחושים של: **{user_to_edit}**")

    # טעינת הניחושים של המשתמש הנבחר
    user_obj = all_guesses.get(user_to_edit, {})
    effective_guesses = logic.get_effective_guesses(user_obj, config)
    new_guesses = effective_guesses.copy()

    # בדיקה האם הטורניר תומך בתוצאה מדויקת (NBA)
    exact_enabled = getattr(config, "IS_EXACT_ENABLED", False)
    tournament_started = len(actual_results) > 0

    if tournament_started:
        st.warning("הטורניר כבר התחיל! שינוי ניחושים כעת ייחשב כ'תיקון' ויגרור ניקוד מופחת.")

    # --- 2. מעבר על שלבי הטורניר והצגת המשחקים ---
    for idx, stage in enumerate(config.STAGES):
        st.write("---")
        st.subheader(config.ROUND_DICT.get(stage, stage))

        # שליפת המשחקים הרלוונטיים לשלב
        stage_matches = list(config.TEAMS.keys()) if idx == 0 else [m for m in config.BRACKET_STRUCTURE if
                                                                    m.startswith(stage)]

        for m_id in stage_matches:
            actual_val_raw = actual_results.get(m_id)
            actual_winner = logic.get_winner_name(actual_val_raw)

            guess_val_raw = effective_guesses.get(m_id)
            current_guess_winner = logic.get_winner_name(guess_val_raw)
            current_guess_score = logic.get_winner_result(guess_val_raw)

            # א. האם המשחק כבר הוכרע ע"י האדמין?
            if actual_winner and actual_winner != logic.NOT_DETERMINED:
                new_guesses[m_id] = guess_val_raw or actual_val_raw

                score_str = f" ({current_guess_score} משחקים)" if current_guess_score else ""
                guess_info = f" (ניחוש שלך: {current_guess_winner}{score_str})" if current_guess_winner else ""

                actual_score = logic.get_winner_result(actual_val_raw)
                actual_score_str = f" [{actual_score}]" if actual_score else ""

                st.write(
                    f"**{config.ROUND_DICT.get(m_id, m_id)}:** תוצאה סופית: **{actual_winner}**{actual_score_str}{guess_info} 🔒")
                continue

            # ב. חישוב משתתפים אפשריים לפי ניחושים קודמים
            participants = logic.get_participant_teams(m_id, new_guesses, actual_results, config)

            if logic.NOT_DETERMINED not in participants:
                # התראה על ניחוש שבור (דורש תיקון)
                if current_guess_winner and current_guess_winner != logic.NOT_DETERMINED and current_guess_winner not in participants:
                    st.error(f"⚠️ **דרוש תיקון:** ניחשת ש-{current_guess_winner} תנצח, אך היא לא משתתפת במשחק זה.")

                # בחירת מנצחת
                default_idx = participants.index(current_guess_winner) if current_guess_winner in participants else 0
                chosen_winner = st.radio(f"מנצחת - {config.ROUND_DICT.get(m_id, m_id)}:",
                                         participants, index=default_idx, key=f"r_win_{user_to_edit}_{m_id}")

                # בחירת תוצאה מדויקת (במידה ומופעל ב-Config)
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
                st.info(f"{config.ROUND_DICT.get(m_id, m_id)}: ממתין לתוצאות משלבים קודמים...")

    # --- 3. שמירת הניחושים ---
    st.write("---")
    if st.button("💾 שמור ניחושים", use_container_width=True):
        # קביעת ה-Bucket (האם זה ניחוש בסיס או תיקון מאוחר)
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
        st.success(f"הניחושים של {user_to_edit} נשמרו בהצלחה!")
        st.rerun()