# migration script to move data sources from local JSON files to the Supabase DB cloud
# Executed successfully on 16.4.26

import json
import os
import data_manager

def migrate_all():
    print("🚀 מתחיל מיגרציה מלאה ל-Supabase...")

    # 1. העלאת משתמשים (קובץ גלובלי)
    if os.path.exists("../data/users_auth.json"):
        with open("../data/users_auth.json", "r", encoding="utf-8") as f:
            data_manager.save_users(json.load(f))
            print("✅ משתמשים הועלו.")

    # 2. סריקת תיקיות הטורנירים
    for item in os.listdir("../data"):
        item_path = os.path.join("../data", item)
        if os.path.isdir(item_path):
            comp_id = item
            print(f"\n📦 מעבד טורניר: {comp_id}")

            # תוצאות אמת
            if os.path.exists(f"{item_path}/actual_results.json"):
                with open(f"{item_path}/actual_results.json", "r") as f:
                    data_manager.save_actual_results(comp_id, json.load(f))
                print(f"  - תוצאות אמת סונכרנו")

            # ניחושים
            if os.path.exists(f"{item_path}/user_guesses.json"):
                with open(f"{item_path}/user_guesses.json", "r") as f:
                    guesses = json.load(f)
                    for user, data in guesses.items():
                        data_manager.save_user_guess(comp_id, user, data)
                print(f"  - ניחושים של {len(guesses)} משתמשים סונכרנו")

            # קאש AI
            if os.path.exists(f"{item_path}/ai_commentary_history.json"):
                with open(f"{item_path}/ai_commentary_history.json", "r") as f:
                    data_manager.save_commentary_cache(comp_id, json.load(f))
                print(f"  - היסטוריית פרשן סונכרנה")

            if os.path.exists(f"{item_path}/ai_rules_cache.json"):
                with open(f"{item_path}/ai_rules_cache.json", "r") as f:
                    data_manager.save_ai_cache(comp_id, json.load(f))
                print(f"  - קאש חוקים סונכרן")

    print("\n✨ הכל מוכן! כל הנתונים נמצאים ב-Supabase.")

if __name__ == "__main__":
    migrate_all()