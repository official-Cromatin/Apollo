from datetime import datetime

def get_elapsed_time(timestamp:float) -> str:
    """Convert an timestamp into an predefined elapsed time format (00min 00sec), without miliseconds"""
    time_elapsed = datetime.fromtimestamp(timestamp)
    return f"{time_elapsed.minute // 60}min {time_elapsed.second:02}sec"

def get_elapsed_time_ms(timestamp:float) -> str:
    """Convert an timestamp into an predefined elapsed time format (00min 00sec 000ms), with miliseconds"""
    time_elapsed = datetime.fromtimestamp(timestamp)
    return f"{time_elapsed.minute // 60}min {time_elapsed.second:02}sec {time_elapsed.microsecond // 1000}ms"

def get_elapsed_time_smal(timestamp:float) -> str:
    """Convert an timestamp into an predefined elapsed time format (00sec 000ms)"""
    time_elapsed = datetime.fromtimestamp(timestamp)
    return f"{time_elapsed.second:02}sec {time_elapsed.microsecond // 1000:03}ms"

def get_elapsed_time_big(timestamp:float) -> str:
    """Convert an timestamp into an predefined elapsed time format (00days 00hrs 00min)"""
    time_elapsed = datetime.fromtimestamp(timestamp)
    return f"{time_elapsed.day - 1}days {time_elapsed.hour - 1}hrs {1 if time_elapsed.minute == 0 else time_elapsed.minute}min"

def get_elapsed_time_milliseconds(timestamp:float) -> str:
    """Convert an timestamp into an predefined elapsed time format (0000ms)"""
    time_elapsed = datetime.fromtimestamp(timestamp)
    return f"{time_elapsed.second * 1000 + time_elapsed.microsecond // 1000}ms"