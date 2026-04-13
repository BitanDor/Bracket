# tournaments/nba_2026_config.py

ID = "nba_2026"
NAME = "NBA Playoffs 2026"
STAGES = ["PLAY_IN_1", "PLAY_IN_2", "R1", "CONF_SEMIS", "CONF_FINALS", "FINALS"]

TEAMS = {
    "PLAY_IN_1_E_7vs8": ["Philadelphia 76ers", "Orlando Magic"],
    "PLAY_IN_1_E_9vs10": ["Charlotte Hornets", "Miami Heat"],
    "PLAY_IN_1_W_7vs8": ["Phoenix Suns", "Portland Trail Blazers"],
    "PLAY_IN_1_W_9vs10": ["LA Clippers", "Golden State Warriors"]
}

BRACKET_STRUCTURE = {
    # שלב פליי-אין 2: הקרב על סיד 8 (תלוי בתוצאות של PLAY_IN_1)
    "PLAY_IN_2_E_FOR_8": ["L_PLAY_IN_1_E_7vs8", "PLAY_IN_1_E_9vs10"],
    "PLAY_IN_2_W_FOR_8": ["L_PLAY_IN_1_W_7vs8", "PLAY_IN_1_W_9vs10"],

    # סיבוב ראשון - מזרח (ניזון מתוצאות הפליי-אין)
    "R1_E1": ["Detroit Pistons", "PLAY_IN_2_E_FOR_8"],
    "R1_E2": ["Boston Celtics", "PLAY_IN_1_E_7vs8"],
    "R1_E3": ["NY Knicks", "Atlanta Hawks"],
    "R1_E4": ["Cleveland Cavaliers", "Toronto Raptors"],

    # סיבוב ראשון - מערב
    "R1_W1": ["OKC Thunder", "PLAY_IN_2_W_FOR_8"],
    "R1_W2": ["SA Spurs", "PLAY_IN_1_W_7vs8"],
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
    "PLAY_IN_1": "פליי-אין: שלב 1",
    "PLAY_IN_2": "פליי-אין: שלב הכרעה",
    "R1": "סיבוב ראשון",
    "CONF_SEMIS": "חצי גמר אזורי",
    "CONF_FINALS": "גמר אזורי",
    "FINALS": "גמר ה-NBA",
    "PLAY_IN_1_E_7vs8": "מזרח: קרב על סיד 7",
    "PLAY_IN_1_E_9vs10": "מזרח: 9 נגד 10",
    "PLAY_IN_1_W_7vs8": "מערב: קרב על סיד 7",
    "PLAY_IN_1_W_9vs10": "מערב: 9 נגד 10",
    "PLAY_IN_2_E_FOR_8": "מזרח: קרב על סיד 8",
    "PLAY_IN_2_W_FOR_8": "מערב: קרב על סיד 8"
}

POINTS_MAP = {
    "FINALS":      {"BASE": 16, "PLAY_IN_1": 8, "PLAY_IN_2": 8, "R1": 4, "CONF_SEMIS": 2, "CONF_FINALS": 1},
    "CONF_FINALS": {"BASE": 8, "PLAY_IN_1": 4,  "PLAY_IN_2": 4, "R1": 2, "CONF_SEMIS": 1},
    "CONF_SEMIS":  {"BASE": 4, "PLAY_IN_1": 2,   "PLAY_IN_2": 2, "R1": 1},
    "R1":          {"BASE": 2, "PLAY_IN_1": 1,   "PLAY_IN_2": 1},
    "PLAY_IN_2":   {"BASE": 1, "PLAY_IN_1": 1},
    "PLAY_IN_1":   {"BASE": 1}
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
    "columns_width": [0.7, 0.7, 0.8, 0.8, 0.8, 1],
    "spacers": {
        "R1": {"top": 1.5, "between": 3},
        "CONF_SEMIS": {"top": 6.5, "between": 12.5},
        "CONF_FINALS": {"top": 15, "between": 32},
        "FINALS": {"top": 36}
    }
}