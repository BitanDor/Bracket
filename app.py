# app.py
import streamlit as st
import streamlit_authenticator as stauth
import data_manager
import tournaments


def main():
    st.set_page_config(page_title="Bitan's Bracket", layout="wide", page_icon="🏆")

    # --- 1. טעינה דינמית של כל הטורנירים הזמינים ---
    AVAILABLE_TOURNAMENTS = tournaments.load_all_configs()

    # --- 2. בחירת טורניר (גלוי לכולם) ---
    col1, _ = st.columns([1, 4])
    with col1:
        comp_id = st.selectbox("בחר תחרות:",
                               list(AVAILABLE_TOURNAMENTS.keys()),
                               format_func=lambda x: AVAILABLE_TOURNAMENTS[x].NAME)

    config = AVAILABLE_TOURNAMENTS[comp_id]

    # --- 3. טעינת נתונים (משתמשים גלובליים, נתוני טורניר מקומיים) ---
    users_auth = data_manager.load_users()  # גלובלי
    all_guesses = data_manager.load_all_guesses(comp_id)  # לפי טורניר
    actual_results = data_manager.load_actual_results(comp_id)  # לפי טורניר

    # --- 4. מערכת אימות גלובלית ---
    authenticator = stauth.Authenticate(
        users_auth,
        "bracket_global_cookie",  # עוגייה אחת לכל האתר
        st.secrets["AUTH_SIGNATURE_KEY"],
        cookie_expiry_days=30
    )

    authenticator.login(location='sidebar')

    auth_status = st.session_state.get("authentication_status")
    username = st.session_state.get("username")
    name = st.session_state.get("name")

    # --- 5. ניהול טאבים והרשאות ---
    st.title(f"Bitan's Bracket - {config.NAME} 🏆")

    tabs_labels = ["🌳 עץ הטורניר", "📜 תקנון"]
    if auth_status:
        tabs_labels.insert(1, "✍️ הניחושים שלי")
        user_role = users_auth['usernames'][username].get('role', 'user')
        if user_role == "admin":
            tabs_labels.insert(2, "⚙️ ניהול (Admin)")

    tabs = st.tabs(tabs_labels)

    # --- 6. רינדור טאבים ---
    with tabs[0]:
        from tree_tab import render_tree_tab
        render_tree_tab(all_guesses, actual_results, config)

    if auth_status:
        user_role = users_auth['usernames'][username].get('role', 'user')
        with tabs[1]:
            from add_tab import render_add_tab
            render_add_tab(all_guesses, actual_results, config, comp_id, username, user_role)

        if user_role == "admin":
            with tabs[2]:
                from admin_tab import render_admin_tab
                render_admin_tab(actual_results, config, comp_id)

    with tabs[-1]:
        user_role = users_auth['usernames'][username].get('role', 'user') if auth_status else 'guest'
        from tab_rules import render_rules_tab
        render_rules_tab(config, actual_results, user_role)

    # --- 7. סיידבר ---
    with st.sidebar:
        if auth_status:
            st.success(f"שלום, {name}!")
            authenticator.logout('התנתקות', 'sidebar')
        elif auth_status is False:
            st.error('שם משתמש או סיסמה שגויים')

        st.write("---")
        from sidebar import render_sidebar
        render_sidebar(all_guesses, actual_results, config)


if __name__ == "__main__":
    main()