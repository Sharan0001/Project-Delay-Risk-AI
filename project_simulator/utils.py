import random
from typing import Tuple


def chance(prob: float) -> bool:
    """
    Returns True with probability = prob
    """
    return random.random() < prob


def random_delay(min_days: int, max_days: int) -> int:
    """
    Random integer delay in [min_days, max_days]
    """
    return random.randint(min_days, max_days)


def regress_progress(current: float, max_regression: float = 0.2) -> float:
    """
    Simulates rework by reducing progress.
    Ensures progress does not go below 0.
    """
    regression = random.uniform(0.05, max_regression)
    return max(0.0, current - regression)
