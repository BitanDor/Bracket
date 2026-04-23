# executed 23.4 to create teams in the system (local)

import json
import uuid6
from domain.models import Team
import tournaments.nba_2026_config as nba_cfg
import tournaments.ucl_2026_config as ucl_cfg


def migrate_teams():
    print("🚀 Starting Team migration to Domain Models v2...")

    unified_teams = {}

    # 1. NBA
    # NBA TEAM_FLAGS team_emoji
    for name, emoji in nba_cfg.TEAM_FLAGS.items():
        print(name)
        if name not in unified_teams:
            unified_teams[name] = {
                "name": name,
                "emoji": emoji,
                "flag": "🇺🇸",  # ברירת מחדל ל-NBA
                "image": f"assets/teams/nba/{name.lower().replace(' ', '_')}.png"
            }

    # 2. עיבוד קבוצות UCL
    # ב-UCL הדגל נשמר ב-TEAM_FLAGS. נשים אותו בשדה team_national_flag
    for name, flag in ucl_cfg.TEAM_FLAGS.items():
        if name in unified_teams:
            # אם הקבוצה כבר קיימת (למשל משחקי ידידות עתידיים), נעדכן רק את הדגל
            unified_teams[name]["flag"] = flag
        else:
            unified_teams[name] = {
                "name": name,
                "emoji": "⚽",  # ברירת מחדל ל-UCL
                "flag": flag,
                "image": f"assets/teams/ucl/{name.lower().replace(' ', '_')}.png"
            }

    # 3. יצירת אובייקטי Team ושמירה ל-JSON
    final_teams_db = {}
    for name, data in unified_teams.items():
        t_id = uuid6.uuid7()

        team_obj = Team(
            team_id=t_id,
            team_name=data["name"],
            team_emoji=data["emoji"],
            team_national_flag=data["flag"],
            team_image_file_location=data["image"]
        )
        print(team_obj)

        # שמירה לפי ה-UUID כמפתח (casting ל-string עבור ה-JSON)
        final_teams_db[str(t_id)] = team_obj.model_dump(mode='json')

    # שמירה לתיקייה המקומית החדשה
    print(final_teams_db)
    import os
    os.makedirs("local_scripts/data/v2_local", exist_ok=True)

    with open("local_scripts/data/v2_local/teams.json", "w", encoding="utf-8") as f:
        json.dump(final_teams_db, f, indent=4, ensure_ascii=False)

    print(f"✅ Successfully migrated {len(final_teams_db)} teams to data/v2_local/teams.json")


if __name__ == "__main__":
    migrate_teams()