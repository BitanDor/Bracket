# TO EXECUTE: streamlit run app.py

import streamlit as st
import data_manager
from tournaments import ucl_2026_config, nba_2026_config
from admin_tab import render_admin_tab
from tree_tab import render_tree_tab
from add_tab import render_add_tab
from sidebar import render_sidebar
from tab_rules import render_rules_tab

# רישום התחרויות הזמינות
AVAILABLE_TOURNAMENTS = {
    ucl_2026_config.ID: ucl_2026_config,
    nba_2026_config.ID: nba_2026_config
}


def main():
    st.set_page_config(page_title="Bitan's Bracket", layout="wide", page_icon="🏆")

    # --- 1. בחירת תחרות ---
    col1, _ = st.columns([1, 4])
    with col1:
        comp_id = st.selectbox("בחר תחרות:", list(AVAILABLE_TOURNAMENTS.keys()),
                               format_func=lambda x: AVAILABLE_TOURNAMENTS[x].NAME)

    config = AVAILABLE_TOURNAMENTS[comp_id]
    st.title(f"Bitan's Bracket - {config.NAME} 🏆")

    # --- 2. טעינת נתונים ---
    all_guesses = data_manager.load_all_guesses(comp_id)
    actual_results = data_manager.load_actual_results(comp_id)

    # --- 3. סיידבר: טבלת ניקוד ---
    render_sidebar(all_guesses, actual_results, config)

    # --- 4. טאבים בממשק הראשי ---
    tab_tree, tab_add, tab_admin, tab_rules = st.tabs([
        "🌳 עץ הטורניר",
        "✍️ ניחושים",
        "⚙️ ניהול",
        "📜 תקנון"
    ])

    with tab_tree:
        render_tree_tab(all_guesses, actual_results, config)

    with tab_add:
        render_add_tab(all_guesses, actual_results, config, comp_id)

    with tab_admin:
        render_admin_tab(actual_results, config, comp_id)

    with tab_rules:
        render_rules_tab(config, actual_results)


if __name__ == "__main__":
    main()