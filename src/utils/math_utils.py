from typing import TypeVar

T = TypeVar("T", int, float)


def clamp(value: T, min_value: T, max_value: T) -> T:
    return max(min_value, min(value, max_value))
