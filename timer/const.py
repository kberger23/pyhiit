from pathlib import Path

DEBUG = False
DEBUG_INTERVAL_TIME = 1

EXERCISE_JSON = Path(__file__).parents[0]/"../exercises/exercises.json"
if DEBUG:
    EXERCISE_HISTORY_JSON = Path(__file__).parents[0]/"../exercises/history.debug.json"
else:
    EXERCISE_HISTORY_JSON = Path(__file__).parents[0]/"../exercises/history.json"
