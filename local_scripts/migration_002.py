# Migration script to add user_id values to users and guess tables.
# Executed successfully on 17.4.26 20:55

import data_manager


def run_id_migration():
    print("🚀 מתחיל מיגרציית IDs למשתמשים...")

    # 1. טעינת נתוני המשתמשים הנוכחיים מה-DB
    users_auth = data_manager.load_users()
    usernames_dict = users_auth.get("usernames", {})

    # מיפוי שיעזור לנו לעדכן את טבלת הניחושים אחר כך
    name_to_id_map = {}

    # 2. יצירת IDs רצים ועדכון המילון
    for i, (name, details) in enumerate(usernames_dict.items(), 1):
        uid = f"user_{i:03d}"  # יוצר user_001, user_002 וכו'
        details["uid"] = uid
        name_to_id_map[name] = uid
        print(f"  - משתמש {name} קיבל ID: {uid}")

    # 3. שמירת המשתמשים המעודכנים ל-Supabase
    data_manager.save_users(users_auth)
    print("✅ טבלת users_auth עודכנה עם IDs.")

    # 4. עדכון טבלת user_guesses - קישור הניחושים ל-ID במקום לשם
    supabase = data_manager.get_client()
    all_guesses_raw = supabase.table("user_guesses").select("*").execute()

    for row in all_guesses_raw.data:
        username = row['username']
        if username in name_to_id_map:
            uid = name_to_id_map[username]
            # עדכון עמודת ה-user_id ב-DB
            supabase.table("user_guesses").update({"user_id": uid}).eq("id", row['id']).execute()
            print(f"  - הניחוש של {username} קושר ל-ID: {uid}")

    print("\n✨ המיגרציה הסתיימה בהצלחה!")


if __name__ == "__main__":
    run_id_migration()