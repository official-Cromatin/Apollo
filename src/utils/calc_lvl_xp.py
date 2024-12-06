import math

def calculate_current_level_experience(current_level:int) -> int:
    """Calculates the amount of experience required to complete this level"""
    return int(5 * math.pow(current_level, 2) + 50 * current_level + 100)

def calculate_total_level_experience(target_level:int) -> int:
    """Calculates the total XP required to reach (not complete) a certain level"""
    if target_level <= 0:
        return 0
    return int((5 / 3) * math.pow(target_level, 3) + 
               (45 / 2) * math.pow(target_level, 2) + 
               (455 / 6) * target_level)