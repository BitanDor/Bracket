# tab_rules.py
import streamlit as st
from google import genai
import os
from data_manager import load_ai_cache, save_ai_cache


# פונקציה לקבלת טבלת ניקוד מעוצבת בעזרת Gemini
@st.cache_data
def get_ai_scoring_table(points_map, round_dict):
    # שליפת המפתח מ-Streamlit Secrets או ממשתנה סביבה
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return "⚠️ שגיאה: לא הוגדר GEMINI_API_KEY במערכת. לא ניתן להפיק את טבלת הניקוד בעזרת AI."

    client = genai.Client(api_key=api_key)

    # בניית הפרומפט - נותנים ל-Gemini את המידע הגולמי ואת התרגומים
    prompt = f"""
    קח את המידע הגולמי הבא על שיטת הניקוד בטורניר בראקט (Bracket) והפוך אותו לטבלת Markdown מקצועית, ברורה ומעוצבת בעברית.

    הסבר קצר על השיטה:
    1. הניקוד בטורניר מוכפל בכל שלב (ככל שהשלב מתקדם יותר, הניקוד גבוה יותר).
    2. 'BASE' מייצג ניקוד על ניחוש נכון שבוצע לפני שהטורניר התחיל (הניקוד המקסימלי).
    3. מפתחות כמו 'R1' או 'CONF_SEMIS' מייצגים את חלון הזמן שבו בוצע תיקון לניחוש. אם בוצע תיקון אחרי שלב מסוים, הניקוד על הניחוש יורד בהתאם.

    מילון הניקוד הגולמי (POINTS_MAP):
    {points_map}

    תרגום שמות השלבים (ROUND_DICT):
    {round_dict}

    דרישות:
    - הצג את המידע כטבלה שבה השורות הן השלבים בטורניר והעמודות הן 'ניקוד מקורי' ו'ניקוד לאחר תיקון' (פרט לפי שלבי התיקון).
    - השתמש בשמות העבריים מתוך ה-ROUND_DICT.
    - הוסף הסבר קצר מתחת לטבלה על חשיבות הניחוש המקורי מול התיקון.
    - כתוב בטון ספורטיבי ומזמין.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"⚠️ שגיאה בחיבור ל-Gemini: {str(e)}"


def render_rules_tab(config, actual_results):
    st.header("📜 תקנון וכללי הטורניר")

    # 1. הרשמה
    st.subheader("👥 רישום משתתפים")
    tournament_started = len(actual_results) > 0
    if tournament_started:
        st.info("הטורניר כבר החל. לא ניתן להוסיף משתתפים חדשים.")
    else:
        st.success("הטורניר טרם החל! ניתן להוסיף משתתפים חדשים בטאב 'ניהול ניחושים'.")

    # 2. עריכת ניחושים
    st.subheader("✍️ עריכת ניחושים")
    st.markdown("""
    * ניתן לערוך ניחושים בכל שלב, כל עוד **תוצאת האמת לאותו משחק טרם הוזנה**.
    * **שימו לב:** עריכת ניחוש לאחר שהטורניר התחיל נחשבת כ'תיקון'. תיקונים מזכים ב**ניקוד מופחת** בהשוואה לניחוש המקורי שבוצע לפני תחילת הטורניר.
    * ככל שהתיקון מבוצע בשלב מאוחר יותר של הטורניר, הניקוד הפוטנציאלי על אותו משחק יורד.
    """)

    # 3. טבלת ניקוד (מופקת בעזרת AI)
    st.subheader("📊 שיטת הניקוד (מופק בעזרת Gemini AI)")
    recent_points_map = config.POINTS_MAP
    rules_cache = load_ai_cache(config.ID)
    cached_points_map = rules_cache.get("points_map")
    cached_response = str(rules_cache.get("response"))
    if str(cached_points_map) != str(recent_points_map):
        with st.spinner("Gemini מחשב ומעצב את טבלת הניקוד..."):
                ai_table = get_ai_scoring_table(recent_points_map, config.ROUND_DICT)
                cache_data = {
                    "points_map": recent_points_map,
                    "response": ai_table,
                }
                save_ai_cache(config.ID, cache_data)
    else:
        ai_table = cached_response
    st.markdown(ai_table)