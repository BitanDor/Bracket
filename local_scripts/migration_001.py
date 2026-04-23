import data_manager

def fix_json_keys():
    users_auth = data_manager.load_users()
    for name, details in users_auth["usernames"].items():
        if "uid" in details:
            details["user_id"] = details.pop("uid")
    data_manager.save_users(users_auth)
    print("✅ המפתח uid הוחלף ב-user_id בכל רשומות המשתמשים!")

if __name__ == "__main__":
    fix_json_keys()