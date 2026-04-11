# tournaments/nba_2026_config.py

ID = "nba_2026"
NAME = "NBA Playoffs 2026"
STAGES = ["PLAY_IN", "R1", "CONF_SEMIS", "CONF_FINALS", "FINALS"]

# שלב הבסיס: משחקי פליי-אין
TEAMS = {
    # מזרח
    "PLAY_IN_E_7vs8": ["East Team #7", "East Team #8"],
    "PLAY_IN_E_9vs10": ["East Team #9", "East Team #10"],
    # מערב
    "PLAY_IN_W_7vs8": ["West Team #7", "West Team #8"],
    "PLAY_IN_W_9vs10": ["West Team #9", "West Team #10"]
}

BRACKET_STRUCTURE = {
    # השלמת שלב הפליי-אין (קרב על סיד 8)
    "PLAY_IN_E_FOR_8": ["L_PLAY_IN_E_7vs8", "PLAY_IN_E_9vs10"],
    "PLAY_IN_W_FOR_8": ["L_PLAY_IN_W_7vs8", "PLAY_IN_W_9vs10"],

    # סיבוב ראשון - מזרח
    "R1_E1": ["East Team #1", "PLAY_IN_E_FOR_8"],
    "R1_E2": ["East Team #2", "PLAY_IN_E_7vs8"],
    "R1_E3": ["East Team #3", "East Team #6"],
    "R1_E4": ["East Team #4", "East Team #5"],

    # סיבוב ראשון - מערב
    "R1_W1": ["West Team #1", "PLAY_IN_W_FOR_8"],
    "R1_W2": ["West Team #2", "PLAY_IN_W_7vs8"],
    "R1_W3": ["West Team #3", "West Team #6"],
    "R1_W4": ["West Team #4", "West Team #5"],

    # חצי גמר אזורי (Conference Semis)
    "CONF_SEMIS_E1": ["R1_E1", "R1_E4"],
    "CONF_SEMIS_E2": ["R1_E2", "R1_E3"],
    "CONF_SEMIS_W1": ["R1_W1", "R1_W4"],
    "CONF_SEMIS_W2": ["R1_W2", "R1_W3"],

    # גמר אזורי (Conference Finals)
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

POINTS_MAP = {
    "FINALS": {"BASE": 16, "PLAY_IN": 8, "R1": 4, "CONF_SEMIS": 2, "CONF_FINALS": 1},
    "CONF_FINALS": {"BASE": 8, "PLAY_IN": 4, "R1": 2, "CONF_SEMIS": 1},
    "CONF_SEMIS": {"BASE": 4, "PLAY_IN": 2, "R1": 1},
    "R1": {"BASE": 2, "PLAY_IN": 1},
    "PLAY_IN": {"BASE": 1}
}

TEAM_FLAGS = {} # ניתן להוסיף לוגואים של קבוצות NBA כאן

UI_CONFIG = {
    "columns_width": [0.8, 0.8, 0.8, 0.8, 1],
    "spacers": {
        "PLAY_IN": {"top": 0, "between": 3},
        "R1": {"top": 1.5, "between": 3},
        "CONF_SEMIS": {"top": 5.5, "between": 11},
        "CONF_FINALS": {"top": 12, "between": 24},
        "FINALS": {"top": 28}
    }
}