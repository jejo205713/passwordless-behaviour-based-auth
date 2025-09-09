# modules/typing_analyzer.py

import pandas as pd
from . import user_manager

TYPING_TOLERANCE_SECONDS = 3.0 

def calculate_average(durations: list) -> float | None:
    """
    Calculates the average speed from a list of durations. Does NOT save anything.
    """
    if durations and isinstance(durations, list):
        return sum(durations) / len(durations)
    return None

def verify_typing_speed(email: str, attempt_duration: float) -> bool:
    """
    Verifies if a new typing duration is within the user's normal range.
    """
    baseline = user_manager.get_typing_baseline(email)
    if not (baseline and baseline.get('average_speed')):
        return False

    if pd.isna(baseline['average_speed']):
        return False
        
    avg_speed = baseline['average_speed']
    lower_bound = avg_speed - TYPING_TOLERANCE_SECONDS
    upper_bound = avg_speed + TYPING_TOLERANCE_SECONDS

    print(f"Verifying typing speed for {email}:")
    print(f"  - User's Average: {avg_speed:.2f}s")
    print(f"  - Current Attempt: {attempt_duration:.2f}s")
    print(f"  - Allowed Range: [{lower_bound:.2f}s - {upper_bound:.2f}s]")

    return lower_bound <= attempt_duration <= upper_bound