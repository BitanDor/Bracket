# tournaments/nba_2026_config.py

ID = "nba_2026"
NAME = "NBA Play-offs 2026"

STAGES = ["PLAY_IN", "R1", "CONF_SEMIS", "CONF_FINALS", "FINALS"]

# שלב 1: משחקי הפליי-אין שקובעים את Seed 7 ו-Seed 8
TEAMS = {
    "PLAY_IN_E_7vs8": ["East #7", "East #8"],  # המנצחת היא Seed 7
    "PLAY_IN_E_9vs10": ["East #9", "East #10"],
    "PLAY_IN_W_7vs8": ["West #7", "West #8"],  # המנצחת היא Seed 7
    "PLAY_IN_W_9vs10": ["West #9", "West #10"],

    # משחקי השלמה ל-Seed 8 (המפסידה מ-7vs8 נגד המנצחת מ-9vs10)
    "PLAY_IN_E_FOR_8": ["L_E_7vs8", "W_E_9vs10"],
    "PLAY_IN_W_FOR_8": ["L_W_7vs8", "W_W_9vs10"]
}

BRACKET_STRUCTURE = {
    # סיבוב ראשון מזרח
    "R1_E1": ["East #1", "PLAY_IN_E_FOR_8"],  # 1 נגד Seed 8
    "R1_E2": ["East #2", "PLAY_IN_E_7vs8"],  # 2 נגד Seed 7
    "R1_E3": ["East #3", "East #6"],
    "R1_E4": ["East #4", "East #5"],

    # סיבוב ראשון מערב
    "R1_W1": ["West #1", "PLAY_IN_W_FOR_8"],
    "R1_W2": ["West #2", "PLAY_IN_W_7vs8"],
    "R1_W3": ["West #3", "West #6"],
    "R1_W4": ["West #4", "West #5"],

    # חצי גמר אזורי
    "CONF_SEMIS_E1": ["R1_E1", "R1_E4"],
    "CONF_SEMIS_E2": ["R1_E2", "R1_E3"],
    "CONF_SEMIS_W1": ["R1_W1", "R1_W4"],
    "CONF_SEMIS_W2": ["R1_W2", "R1_W3"],

    # גמר אזורי
    "CONF_FINALS_E": ["CONF_SEMIS_E1", "CONF_SEMIS_E2"],
    "CONF_FINALS_W": ["CONF_SEMIS_W1", "CONF_SEMIS_W2"],

    # גמר ה-NBA
    "FINALS": ["CONF_FINALS_E", "CONF_FINALS_W"]
}

ROUND_DICT = {
    "PLAY_IN": "פליי-אין",
    "R1": "סיבוב ראשון",
    "CONF_SEMIS": "חצי גמר אזורי",
    "CONF_FINALS": "גמר אזורי",
    "FINALS": "גמר ה-NBA",
    # תרגום שמות משחקים ספציפיים
    "PLAY_IN_E_7vs8": "מזרח: קרב על סיד 7",
    "PLAY_IN_E_FOR_8": "מזרח: קרב על סיד 8",
    "R1_E1": "מזרח: 1 נגד 8"
}

POINTS_MAP = {
    "FINALS": {"BASE": 16, "PLAY_IN": 8, "R1": 4, "CONF_SEMIS": 2, "CONF_FINALS": 1},
    "CONF_FINALS": {"BASE": 8, "PLAY_IN": 4, "R1": 2, "CONF_SEMIS": 1},
    "CONF_SEMIS": {"BASE": 4, "PLAY_IN": 2, "R1": 1},
    "R1": {"BASE": 2, "PLAY_IN": 1},
    "PLAY_IN": {"BASE": 1}
}

TEAM_FLAGS = {
    "East #1": "🏀", "West #1": "🏀"  # כאן תכניס את שמות הקבוצות האמיתיות כשיתבררו
}

UI_CONFIG = {
    "columns_width": [1, 1, 1, 1, 1.2],
    "spacers": {
        "PLAY_IN": {"top": 0, "between": 2},
        "R1": {"top": 2, "between": 4},
        "CONF_SEMIS": {"top": 6, "between": 12},
        "CONF_FINALS": {"top": 14, "between": 28},
        "FINALS": {"top": 30}
    }
}