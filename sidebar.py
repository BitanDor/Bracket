import streamlit as st
import pandas as pd
import logic


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