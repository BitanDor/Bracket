# constants.py
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

ROUND_POINTS = {"R16": 1, "QF": 2, "SF": 4, "FINAL": 8}

APP_TITLE = "UCL Predictor 2026"