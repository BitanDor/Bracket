# executed 23.4 to create new user objects for v2
import json
import uuid6
from domain.models import User, UserRole

# Constants for our new IDs (Stable for the local test phase)
UCL_2026_ID = "019dbbe0-fb86-771f-8c54-c3f07108f0b4" # uuid6.uuid7()
NBA_2026_ID = "019dbbe0-fb87-7065-96f5-b4e509a4aa74" # uuid6.uuid7()


def migrate_users():
    print("🔄 Starting user migration to Domain Models v2...")

    with open("../data/users_auth.json", "r") as f:
        old_data = json.load(f)

    new_users = {}
    usernames = old_data.get("usernames", {})

    for name, details in usernames.items():
        # Create new Enterprise User object
        u_id = uuid6.uuid7()

        # Determine active tournaments based on your logic
        active_t = {}
        if name in ["Dor", "Alon", "Nir"]:
            active_t[UCL_2026_ID] = {}
            active_t[NBA_2026_ID] = {}
        elif name == "Maor":
            active_t[NBA_2026_ID] = {}
        else:  # Shusha, Ziv, Galya, Bob
            active_t[UCL_2026_ID] = {}

        user_obj = User(
            user_id=u_id,
            username=name,
            first_name=name,  # Placeholder
            last_name="",
            email=f"{name.lower()}@example.com",
            hashed_password=details["password"],
            role=UserRole.ADMIN if details["role"] == "admin" else UserRole.REGULAR,
            active_tournaments=active_t
        )

        new_users[str(u_id)] = user_obj.model_dump(mode='json')

    # Save to new local directory
    import os
    os.makedirs("../data/v2_local", exist_ok=True)

    with open("../data/v2_local/users.json", "w") as f:
        json.dump(new_users, f, indent=4)

    print(f"✅ Created {len(new_users)} users in data/v2_local/users.json")
    print(f"📌 UCL_2026_ID: {UCL_2026_ID}")
    print(f"📌 NBA_2026_ID: {NBA_2026_ID}")


if __name__ == "__main__":
    migrate_users()