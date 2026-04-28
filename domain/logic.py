from datetime import datetime
from typing import List, Optional
from domain.models import Match, MatchGuessData, Stage, ScoringConfig


def find_guess_window_stage(guess_time: datetime, match: Match, stages: List[Stage]) -> Optional[Stage]:
    """מוצאת את האובייקט של השלב שבו בוצע הניחוש לפי חלונות הזמן של המשחק"""
    for stage_id, (start, end) in match.match_guess_time_windows.items():
        if start <= guess_time <= end:
            # מציאת אובייקט השלב לפי ה-ID שלו
            return next((s for s in stages if s.stage_id == stage_id), None)
    return None


def calculate_points(guess: MatchGuessData,
                     match: Match,
                     scoring_config: ScoringConfig,
                     stages: List[Stage]) -> float:
    """מחשבת את הניקוד עבור ניחוש בודד"""

    # 1. בדיקת תוצאה בסיסית (1/X/2)
    if not match.has_ended or guess.score != match.score:
        return 0.0

    # 2. זיהוי השלב שבו המשתמש ביצע את העדכון (לפי חלון הזמן)
    window_stage = find_guess_window_stage(guess.when_edited, match, stages)
    if not window_stage:
        return 0.0

    # 3. זיהוי השלב שבו המשחק עצמו נמצא (למשל 'FINALS')
    current_match_stage = next((s for s in stages if s.stage_id == match.stage_id), None)
    if not current_match_stage:
        return 0.0

    # 4. שליפת הניקוד המתאים מהמפה
    # מחפשים בתוך הניקוד של הגמר את הניקוד שמגיע על ניחוש שבוצע בשלב ה-window_stage
    match_stage_name = current_match_stage.stage_name
    window_stage_name = window_stage.stage_name

    stage_points_options = scoring_config.points_map.get(match_stage_name, {})

    # שליפת הניקוד לפי חלון הזמן שבו בוצע העדכון
    base_points = stage_points_options.get(window_stage_name, 0.0)

    # 5. בונוס תוצאה מדויקת
    if guess.detailed_score and guess.detailed_score == match.detailed_score:
        return base_points * scoring_config.detailed_score_multiplier

    return float(base_points)