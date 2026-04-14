import streamlit as st
import pandas as pd
import logic
import data_manager


def render_sidebar(all_guesses, actual_results, config):
    st.sidebar.header("📊 טבלת ניקוד")
    leaderboard_data = []
    for user, user_obj in all_guesses.items():
        score, _ = logic.calculate_score(user_obj, actual_results, config)
        effective_guesses = logic.get_effective_guesses(user_obj, config)

        # שליפת ניחוש הזוכה ונרמול השם
        winner_raw = effective_guesses.get("FINAL") or effective_guesses.get("FINALS", logic.NOT_DETERMINED)
        winner_name = logic.get_winner_name(winner_raw)

        flag = config.TEAM_FLAGS.get(winner_name, "")
        winner_display = f"{flag} {winner_name}" if winner_name != logic.NOT_DETERMINED else "טרם נקבע"

        leaderboard_data.append({"שם": user, "זוכה": winner_display, "נקודות": score})

    if leaderboard_data:
        df = pd.DataFrame(leaderboard_data).sort_values(by="נקודות", ascending=False)
        df.index = range(1, len(df) + 1)
        df.index.name = "מיקום"
        st.sidebar.table(df)
    else:
        st.sidebar.write("עוד אין ניחושים.")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎙️ פינת הפרשן")

    history = data_manager.load_commentary_cache(config.ID)

    if not history:
        st.sidebar.write("הפרשן נח כרגע. פרשנות תופיע לאחר עדכון התוצאות הבא.")

    for entry in history:
        # הצגת הטקסט
        st.sidebar.info(entry['text'])
        # הצגת התאריך מתחת
        st.sidebar.caption(f"({entry['timestamp']})")
        st.sidebar.markdown("---")