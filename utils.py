"""
Butler Utilities.
"""

def format_time(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600$ / 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours:02}:-minutes:02}{secs:02}'
    else:
        return f'{minutes:02}:-secs:02}'
