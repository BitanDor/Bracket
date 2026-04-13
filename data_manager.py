# TO EXECUTE: streamlit run app.py

import json
import os

def get_file_path(competition_id, filename):
    """מייצר נתיב לתיקיית התחרות ומוודא שהיא קיימת"""
    dir_path = os.path.join("data", competition_id)
    os.makedirs(dir_path, exist_ok=True)
    return os.path.join(dir_path, filename)

def _load_json(file_path, default_value):
    if not os.path.exists(file_path):
        return default_value
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default_value

def _save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_all_guesses(comp_id):
    return _load_json(get_file_path(comp_id, "user_guesses.json"), {})

def save_user_guess(comp_id, user_name, guesses):
    path = get_file_path(comp_id, "user_guesses.json")
    all_guesses = _load_json(path, {})
    all_guesses[user_name] = guesses
    _save_json(path, all_guesses)

def load_actual_results(comp_id):
    return _load_json(get_file_path(comp_id, "actual_results.json"), {})

def save_actual_results(comp_id, results):
    _save_json(get_file_path(comp_id, "actual_results.json"), results)

def delete_all_data(comp_id):
    """פונקציית עזר חדשה לאיפוס תחרות ספציפית"""
    g_path = get_file_path(comp_id, "user_guesses.json")
    r_path = get_file_path(comp_id, "actual_results.json")
    if os.path.exists(g_path): os.remove(g_path)
    if os.path.exists(r_path): os.remove(r_path)