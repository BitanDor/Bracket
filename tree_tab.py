import streamlit as st
import logic
import ui_components


def render_tree_tab(all_guesses, actual_results, config, uid_to_name):
    st.header(" 🌳 עץ הטורניר")
    view_user = st.selectbox(
        "בחר משתתף כדי לראות את העץ שלו:",
        ["תוצאות אמת"] + list(all_guesses.keys()),
        format_func=lambda x: uid_to_name.get(x, x) if x != "תוצאות אמת" else x
    )

    is_actual_view = (view_user == "תוצאות אמת")
    raw_user_obj = {} if is_actual_view else all_guesses.get(view_user, {})
    current_display_guesses = actual_results if is_actual_view else logic.get_effective_guesses(raw_user_obj, config)

    # הפרדת שלבי פליי-אין/מוקדמות
    preliminary_stages = [s for s in config.STAGES if s.startswith("PLAY_IN")]
    main_stages = [s for s in config.STAGES if not s.startswith("PLAY_IN")]
    start_idx = len(preliminary_stages)

    # יצירת העץ המרכזי
    main_cols_width = config.UI_CONFIG["columns_width"][start_idx:]
    if len(main_cols_width) < len(main_stages):
        main_cols_width += [1.0] * (len(main_stages) - len(main_cols_width))

    bracket_cols = st.columns(main_cols_width, gap="medium")

    for idx, stage_key in enumerate(main_stages, start=start_idx):
        with bracket_cols[idx - start_idx]:
            st.subheader(config.ROUND_DICT.get(stage_key, stage_key))
            stage_spacers = config.UI_CONFIG["spacers"].get(stage_key, {})

            if "top" in stage_spacers:
                st.write(f"<div style='height: {stage_spacers['top']}em;'></div>", unsafe_allow_html=True)

            matches_in_stage = [m for m in config.BRACKET_STRUCTURE if m.startswith(stage_key)]
            # בטורניר בלי פליי-אין (כמו UCL), השלב הראשון נלקח מ-TEAMS
            if idx == 0:
                matches_in_stage = list(config.TEAMS.keys())

            for m_id in matches_in_stage:
                st.markdown(ui_components.get_match_box_html(
                    m_id,
                    current_display_guesses.get(m_id),
                    is_actual_view,
                    raw_user_obj,
                    config,
                    current_display_guesses,  # המילון שמשמש לחישוב המשתתפים
                    actual_results  # תוצאות האמת לחישוב מי עלה באמת
                ), unsafe_allow_html=True)

                if "between" in stage_spacers:
                    st.write(f"<div style='height: {stage_spacers['between']}em;'></div>", unsafe_allow_html=True)

    # הצגת פליי-אין למטה בנפרד
    if preliminary_stages:
        st.write("---")
        st.header(f"🏀 Play-In")
        all_pi = list(config.TEAMS.keys()) + [m for m in config.BRACKET_STRUCTURE if m.startswith("PLAY_IN")]
        pi_cols = st.columns(len(all_pi))
        for i, m_id in enumerate(all_pi):
            with pi_cols[i]:
                st.caption(config.ROUND_DICT.get(m_id, m_id))
                st.markdown(ui_components.get_match_box_html(
                    m_id, current_display_guesses.get(m_id), is_actual_view,
                    raw_user_obj, config, current_display_guesses, actual_results
                ), unsafe_allow_html=True)
