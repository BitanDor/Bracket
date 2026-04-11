# tournaments/ucl_2026_config.py

ID = "ucl_2026"
NAME = "UEFA Champions League 2026"

# סדר השלבים בטורניר (משמש את הלוגיקה והניקוד הגנריים)
STAGES = ["R16", "QF", "SF", "FINAL"]

TEAMS = {
    "R16_M1": ["Paris Saint-Germain", "Chelsea"],
    "R16_M2": ["Galatasaray", "Liverpool"],
    "R16_M3": ["Real Madrid", "Manchester City"],
    "R16_M4": ["Atalanta", "Bayern Munich"],
    "R16_M5": ["Newcastle", "Barcelona"],
    "R16_M6": ["Atlético Madrid", "Tottenham"],
    "R16_M7": ["Bodø/Glimt", "Sporting CP"],
    "R16_M8": ["Bayer Leverkusen", "Arsenal"]
}

BRACKET_STRUCTURE = {
    "QF1": ["R16_M1", "R16_M2"],
    "QF2": ["R16_M3", "R16_M4"],
    "QF3": ["R16_M5", "R16_M6"],
    "QF4": ["R16_M7", "R16_M8"],
    "SF1": ["QF1", "QF2"],
    "SF2": ["QF3", "QF4"],
    "FINAL": ["SF1", "SF2"]
}

# מפת ניקוד מתואמת לתחרות
POINTS_MAP = {
    "FINAL": {"BASE": 8, "R16": 4, "QF": 2, "SF": 1},
    "SF": {"BASE": 4, "R16": 2, "QF": 1},
    "QF": {"BASE": 2, "R16": 1},
    "R16": {"BASE": 1}
}

# מילון תרגום לעברית ספציפי לתחרות זו
ROUND_DICT = {f"R16_M{i}": f"שמינית הגמר {i}" for i in range(1, 9)}
ROUND_DICT.update({f"QF{i}": f"רבע הגמר {i}" for i in range(1, 5)})
ROUND_DICT.update({f"SF{i}": f"חצי הגמר {i}" for i in range(1, 3)})
ROUND_DICT.update({
    "R16": "שמינית הגמר",
    "QF": "רבע הגמר",
    "SF": "חצי הגמר",
    "FINAL": "גמר ליגת האלופות"
})

TEAM_FLAGS = {
    "Paris Saint-Germain": "🇫🇷", "Chelsea": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Galatasaray": "🇹🇷",
    "Liverpool": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Real Madrid": "🇪🇸", "Manchester City": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Atalanta": "🇮🇹", "Bayern Munich": "🇩🇪", "Newcastle": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Barcelona": "🇪🇸", "Atlético Madrid": "🇪🇸", "Tottenham": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Bodø/Glimt": "🇳🇴", "Sporting CP": "🇵🇹", "Bayer Leverkusen": "🇩🇪", "Arsenal": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"
}

# --- הגדרות עיצוב UI ששומרות על המרווחים שכיווננת ---
UI_CONFIG = {
    "columns_width": [0.7, 0.7, 0.7, 1],
    "spacers": {
        "QF": {"top": 3.5, "between": 7},
        "SF": {"top": 10.5, "between": 21},
        "FINAL": {"top": 24}
    }
}
