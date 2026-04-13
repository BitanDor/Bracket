# tournaments/nba_2026_config.py

ID = "nba_2026"
NAME = "NBA Playoffs 2026"
STAGES = ["PLAY_IN", "R1", "CONF_SEMIS", "CONF_FINALS", "FINALS"]

# שלב הבסיס בלבד: משחקי פליי-אין
TEAMS = {
    # מזרח
    "PLAY_IN_E_7vs8": ["Philadelphia 76ers", "Orlando Magic"],
    "PLAY_IN_E_9vs10": ["Charlotte Hornets", "Miami Heat"],
    # מערב
    "PLAY_IN_W_7vs8": ["Phoenix Suns", "Portland Trail Blazers"],
    "PLAY_IN_W_9vs10": ["LA Clippers", "Golden State Warriors"]
}

BRACKET_STRUCTURE = {
    # השלמת שלב הפליי-אין (קרב על סיד 8)
    "PLAY_IN_E_FOR_8": ["L_PLAY_IN_E_7vs8", "PLAY_IN_E_9vs10"],
    "PLAY_IN_W_FOR_8": ["L_PLAY_IN_W_7vs8", "PLAY_IN_W_9vs10"],

    # סיבוב ראשון - מזרח
    "R1_E1": ["Detroit Pistons", "PLAY_IN_E_FOR_8"],
    "R1_E2": ["Boston Celtics", "PLAY_IN_E_7vs8"],
    "R1_E3": ["NY Knicks", "Atlanta Hawks"],
    "R1_E4": ["Cleveland Cavaliers", "Toronto Raptors"],

    # סיבוב ראשון - מערב
    "R1_W1": ["OKC Thunder", "PLAY_IN_W_FOR_8"],
    "R1_W2": ["SA Spurs", "PLAY_IN_W_7vs8"],
    "R1_W3": ["Denver Nuggets", "Minnesota Timberwolves"],
    "R1_W4": ["LA Lakers", "Houston Rockets"],

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
    "PLAY_IN": "פליי-אין", "R1": "סיבוב ראשון", "CONF_SEMIS": "חצי גמר אזורי",
    "CONF_FINALS": "גמר אזורי", "FINALS": "גמר ה-NBA",
    "PLAY_IN_E_7vs8": "מזרח: קרב על סיד 7", "PLAY_IN_E_FOR_8": "מזרח: קרב על סיד 8",
    "PLAY_IN_W_7vs8": "מערב: קרב על סיד 7", "PLAY_IN_W_FOR_8": "מערב: קרב על סיד 8"
}

# (שאר הקובץ ללא שינוי...)
POINTS_MAP = {
    "FINALS": {"BASE": 16, "PLAY_IN": 8, "R1": 4, "CONF_SEMIS": 2, "CONF_FINALS": 1},
    "CONF_FINALS": {"BASE": 8, "PLAY_IN": 4, "R1": 2, "CONF_SEMIS": 1},
    "CONF_SEMIS": {"BASE": 4, "PLAY_IN": 2, "R1": 1},
    "R1": {"BASE": 2, "PLAY_IN": 1},
    "PLAY_IN": {"BASE": 1}
}

TEAM_FLAGS = {
    # מזרח
    "Philadelphia 76ers": "🔔",
    "Orlando Magic": "🪄",
    "Charlotte Hornets": "🐝",
    "Miami Heat": "🔥",
    "Detroit Pistons": "⚙️",
    "Boston Celtics": "🍀",
    "NY Knicks": "🗽",
    "Atlanta Hawks": "🦅",
    "Cleveland Cavaliers": "⚔️",
    "Toronto Raptors": "🦖",

    # מערב
    "Phoenix Suns": "☀️",
    "Portland Trail Blazers": "🌲",
    "LA Clippers": "⛵",
    "Golden State Warriors": "🌉",
    "OKC Thunder": "⚡",
    "SA Spurs": "🤠",
    "Denver Nuggets": "⛏️",
    "Minnesota Timberwolves": "🐺",
    "LA Lakers": "🟣🟡",
    "Houston Rockets": "🚀"
}

UI_CONFIG = {
    "columns_width": [0.8, 0.8, 0.8, 0.8, 1],
    "spacers": {
        "PLAY_IN": {"top": 0, "between": 3},
        "R1": {"top": 1.5, "between": 3},
        "CONF_SEMIS": {"top": 6.5, "between": 12.5},
        "CONF_FINALS": {"top": 15, "between": 32},
        "FINALS": {"top": 36}
    }
}