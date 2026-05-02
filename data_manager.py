import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

@st.cache_data(ttl=60)
def load_users():
    supabase = get_client()
    res = supabase.table("users_auth").select("credentials").eq("id", "global").maybe_single().execute()
    return res.data['credentials'] if res and res.data else {"usernames": {}}

@st.cache_data(ttl=60)
def get_uid_to_name_map():
    users_data = load_users()
    usernames = users_data.get("usernames", {})
    return {
        details.get("user_id"): details.get("name") or name
        for name, details in usernames.items()
    }

@st.cache_data(ttl=60)
def load_all_guesses(comp_id):
    supabase = get_client()
    res = supabase.table("user_guesses").select("user_id, guesses").eq("comp_id", comp_id).execute()
    if res and res.data:
        return {item['user_id']: item['guesses'] for item in res.data if item['user_id']}
    return {}

@st.cache_data(ttl=60)
def load_actual_results(comp_id):
    supabase = get_client()
    res = supabase.table("actual_results").select("results").eq("comp_id", comp_id).maybe_single().execute()
    return res.data['results'] if res and res.data else {}

@st.cache_data(ttl=60)
def load_commentary_cache(comp_id):
    supabase = get_client()
    res = supabase.table("ai_commentary").select("history").eq("comp_id", comp_id).maybe_single().execute()
    return res.data['history'] if res and res.data else []

@st.cache_data(ttl=60)
def load_ai_cache(comp_id):
    supabase = get_client()
    res = supabase.table("ai_rules_cache").select("cache_data").eq("comp_id", comp_id).maybe_single().execute()
    return res.data['cache_data'] if res and res.data else {}

def save_users(users_data):
    supabase = get_client()
    data = {"id": "global", "credentials": users_data}
    supabase.table("users_auth").upsert(data, on_conflict="id").execute()

def save_user_guess(comp_id, user_id, guesses):
    supabase = get_client()
    data = {
        "comp_id": comp_id,
        "user_id": user_id,
        "guesses": guesses
    }
    supabase.table("user_guesses").upsert(data, on_conflict="comp_id,user_id").execute()
    st.cache_data.clear()

def save_actual_results(comp_id, results):
    supabase = get_client()
    data = {"comp_id": comp_id, "results": results}
    supabase.table("actual_results").upsert(data, on_conflict="comp_id").execute()
    st.cache_data.clear()

def save_commentary_cache(comp_id, history):
    supabase = get_client()
    data = {"comp_id": comp_id, "history": history}
    supabase.table("ai_commentary").upsert(data, on_conflict="comp_id").execute()
    st.cache_data.clear()

def save_ai_cache(comp_id, cache_data):
    supabase = get_client()
    data = {"comp_id": comp_id, "cache_data": cache_data}
    supabase.table("ai_rules_cache").upsert(data, on_conflict="comp_id").execute()

def delete_all_data(comp_id):
    supabase = get_client()
    # מחיקת נתונים לפי comp_id מכל הטבלאות הרלוונטיות
    tables = ["user_guesses", "actual_results", "ai_commentary", "ai_rules_cache"]
    for table in tables:
        supabase.table(table).delete().eq("comp_id", comp_id).execute()
