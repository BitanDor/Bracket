# ai_commentary.py
import streamlit as st
from google import genai
import logic
import data_manager
from datetime import datetime
import os


def update_tournament_commentary(comp_id, config, all_guesses, actual_results):
    """מייצר פרשנות חדשה ושומר אותה בהיסטוריה"""

    # 1. הכנת הנתונים עבור ה-AI (טבלת ניקוד מקוצרת)
    leaderboard = []
    for user, user_obj in all_guesses.items():
        score, _ = logic.calculate_score(user_obj, actual_results, config)
        leaderboard.append(f"- {user}: {score} points")

    leaderboard_str = "\n".join(leaderboard)
    recent_results = str(actual_results)

    # 2. בניית הפרומפט לפי הדרישות הספציפיות שלך
    prompt = f"""
    אתה פרשן ספורט מקצועי ושנון בטורניר הבראקט שלנו.
    לפניך טבלת הניקוד העדכנית ותוצאות האמת האחרונות.

    טבלת ניקוד:
    {leaderboard_str}

    תוצאות אמת אחרונות (מזהה משחק: מנצחת):
    {recent_results}

    הוראות קריטיות:
    - כתוב בטון ספורטיבי, מזמין ומעט עוקצני/מלהיב.
    - תן רק את התוכן להטמעה באתר, בלי הקדמות כמו "הנה הפרשנות".
    תכתוב את כל התגובה רק בעברית. בלי אנגלית.
    - אל תשתמש במשפטים ארוכים מדי - תרד שורה לעיתים קרובות.
    """

    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",  #
            contents=prompt
        )
        ai_text = response.text
    except Exception:
        # במקרה של שגיאה - הודעה גנרית כפי שביקשת
        ai_text = "התוצאות עודכנו! המאבק על הפסגה מתחמם."

    # 3. שמירה להיסטוריה עם תאריך
    history = data_manager.load_commentary_cache(comp_id)
    new_entry = {
        "text": ai_text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    # הוספה לראש הרשימה (כדי שהחדש יהיה ראשון)
    history.insert(0, new_entry)
    data_manager.save_commentary_cache(comp_id, history)