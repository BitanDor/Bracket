# ai_commentary.py
import streamlit as st
from google import genai
import logic
import data_manager
from datetime import datetime


def _safe_display_name(uid, uid_to_name, fallback_index):
    mapped = uid_to_name.get(uid)
    if not mapped or mapped == uid or mapped.lower().startswith("user_"):
        return f"Participant {fallback_index}"
    return mapped


def _format_result_line(team_name, score):
    if team_name == logic.NOT_DETERMINED:
        return "TBD"
    if score is None:
        return team_name
    return f"{team_name} ({score} games)"


def _is_local_debug_request():
    """Return True only for local Streamlit requests on port 8501."""
    try:
        headers = st.context.headers
    except Exception:
        return False

    host = (headers.get("x-forwarded-host") or headers.get("host") or "").lower()
    origin = (headers.get("origin") or "").lower()
    referer = (headers.get("referer") or "").lower()
    values = f"{host} {origin} {referer}"
    return "localhost:8501" in values or "127.0.0.1:8501" in values


def update_tournament_commentary(comp_id, config, all_guesses, previous_actual_results, updated_actual_results, uid_to_name):
    """Generate AI commentary with score-impact context and save to history."""

    all_match_ids = list(config.TEAMS.keys()) + list(config.BRACKET_STRUCTURE.keys())
    exact_enabled = getattr(config, "IS_EXACT_ENABLED", False)

    display_names = {}
    fallback_counter = 1
    for uid in all_guesses:
        display_names[uid] = _safe_display_name(uid, uid_to_name, fallback_counter)
        if display_names[uid].startswith("Participant "):
            fallback_counter += 1

    previous_scores = {}
    updated_scores = {}
    user_impacts = {}
    changed_matches = []

    for m_id in all_match_ids:
        before_raw = previous_actual_results.get(m_id, logic.NOT_DETERMINED)
        after_raw = updated_actual_results.get(m_id, logic.NOT_DETERMINED)
        before_team = logic.get_winner_name(before_raw)
        after_team = logic.get_winner_name(after_raw)
        before_score = logic.get_winner_result(before_raw)
        after_score = logic.get_winner_result(after_raw)

        if before_team != after_team or before_score != after_score:
            changed_matches.append({
                "match": config.ROUND_DICT.get(m_id, m_id),
                "before": _format_result_line(before_team, before_score),
                "after": _format_result_line(after_team, after_score),
                "m_id": m_id,
            })

    for uid, user_obj in all_guesses.items():
        prev_score, _ = logic.calculate_score(user_obj, previous_actual_results, config)
        new_score, _ = logic.calculate_score(user_obj, updated_actual_results, config)
        previous_scores[uid] = prev_score
        updated_scores[uid] = new_score

        exact_count = 0
        partial_count = 0
        miss_count = 0
        for item in changed_matches:
            m_id = item["m_id"]
            actual_raw = updated_actual_results.get(m_id, logic.NOT_DETERMINED)
            actual_team = logic.get_winner_name(actual_raw)
            actual_score = logic.get_winner_result(actual_raw)

            if actual_team == logic.NOT_DETERMINED:
                continue

            guess_raw, _, _ = logic.get_guess_info(user_obj, m_id, config)
            guess_team = logic.get_winner_name(guess_raw)
            guess_score = logic.get_winner_result(guess_raw)

            if not guess_team or guess_team == logic.NOT_DETERMINED or guess_team != actual_team:
                miss_count += 1
            elif exact_enabled and actual_score is not None:
                if guess_score == actual_score:
                    exact_count += 1
                else:
                    partial_count += 1
            else:
                exact_count += 1

        user_impacts[uid] = {
            "delta": new_score - prev_score,
            "exact": exact_count,
            "partial": partial_count,
            "miss": miss_count,
        }

    def _rank(scores_dict):
        ordered = sorted(scores_dict.items(), key=lambda x: (-x[1], display_names.get(x[0], x[0]).lower()))
        rank_map = {uid: i + 1 for i, (uid, _) in enumerate(ordered)}
        lines = [f"{i + 1}. {display_names.get(uid, uid)} - {score} points" for i, (uid, score) in enumerate(ordered)]
        return rank_map, lines, ordered

    prev_rank_map, prev_lines, _ = _rank(previous_scores)
    new_rank_map, new_lines, ordered_new = _rank(updated_scores)

    changed_matches_lines = "\n".join(
        f"- {item['match']}: {item['before']} -> {item['after']}" for item in changed_matches
    ) or "- No match outcomes changed in this update."

    impact_lines = []
    for uid, _ in ordered_new:
        impact = user_impacts[uid]
        impact_lines.append(
            f"- {display_names.get(uid, uid)}: +{impact['delta']} pts, "
            f"rank {prev_rank_map.get(uid, '-') } -> {new_rank_map.get(uid, '-')}, "
            f"exact={impact['exact']}, partial={impact['partial']}, miss={impact['miss']}"
        )

    prompt = f"""
You are writing a short sports-style bracket commentary for direct website embedding.
Focus mostly on how the leaderboard changed after the latest true-results update.

Important: this response is injected automatically by the following code, so output must be ready-to-render text only:
```python
import streamlit as st
from google import genai
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)
response = client.models.generate_content(
            model="gemini-2.5-flash",  #
            contents=prompt
        )
ai_text = response.text
st.sidebar.markdown("ai_text")
```

Rules for your output:
1) Write ONLY in Hebrew. No English words, no Latin letters, no transliteration. I stress - NO ENGLISH IN RESPONSE!
2) No opening lines such as "here is your commentary", and no ending suggestions 
such as "I can rewrite in another tone", since your response is embedded directly without human review.
3) Focus on storytelling and insights, not just dry facts. Be enthusiastic, and make it engaging and fun to read, 
as if a sports journalist is narrating the drama of the tournament.
4) Keep sentences relatively short and break lines often. If there's not much to say, it's better to have a few impactful lines than a long text.
5) Emphasize ranking movement, points gained, and why players moved up/down.
6) Mention exact hits, partial hits, and misses using the data below.
7) Refer to participants only by the real names provided below.

Latest result changes:
{changed_matches_lines}

Leaderboard BEFORE update:
{chr(10).join(prev_lines)}

Leaderboard AFTER update:
{chr(10).join(new_lines)}

Per-participant impact in this update:
{chr(10).join(impact_lines)}
"""

    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    if _is_local_debug_request():
        print(f"Sending the following prompt to gemini 2.5:\n\n{prompt}")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",  #
            contents=prompt
        )
        ai_text = (response.text or "").strip()
        if not ai_text:
            return False
    except Exception as e:
        st.error(f"AI commentary generation failed: {e}")
        return False

    # 3. שמירה להיסטוריה עם תאריך
    history = data_manager.load_commentary_cache(comp_id)
    new_entry = {
        "text": ai_text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    # הוספה לראש הרשימה (כדי שהחדש יהיה ראשון)
    history.insert(0, new_entry)
    data_manager.save_commentary_cache(comp_id, history)
    return True
