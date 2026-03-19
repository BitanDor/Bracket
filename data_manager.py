import json
import os

# שמות הקבצים שבהם נשמור את המידע
GUESSES_FILE = "user_guesses.json"
RESULTS_FILE = "actual_results.json"

def _load_json(file_path, default_value):
    """פונקציית עזר לטעינת קובץ JSON בבטחה"""
    if not os.path.exists(file_path):
        return default_value
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default_value

def _save_json(file_path, data):
    """פונקציית עזר לשמירת מידע לקובץ JSON"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def save_user_guess(user_name, guesses):
    """
    שומר ניחוש של משתמש.
    אם המשתמש כבר קיים, הניחוש שלו יתעדכן.
    """
    all_guesses = _load_json(GUESSES_FILE, {})
    all_guesses[user_name] = guesses
    _save_json(GUESSES_FILE, all_guesses)

def load_all_guesses():
    """טוען את כל הניחושים של כל המשתמשים"""
    return _load_json(GUESSES_FILE, {})

def save_actual_results(results):
    """עדכון תוצאות האמת של הטורניר (על ידי המנהל)"""
    _save_json(RESULTS_FILE, results)

def load_actual_results():
    """טוען את תוצאות האמת המעודכנות"""
    return _load_json(RESULTS_FILE, {})

def delete_user(user_name):
    """מחיקת משתמש מהטבלה (למקרה של טעויות בשם)"""
    all_guesses = _load_json(GUESSES_FILE, {})
    if user_name in all_guesses:
        del all_guesses[user_name]
        _save_json(GUESSES_FILE, all_guesses)