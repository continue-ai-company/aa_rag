from enum import Enum


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

    def __str__(self):
        return f"{self.value}"


class Car:
    def __init__(self, color: Color | int):
        if isinstance(color, int):
            self.color = Color(color)
        else:
            self.color = color


print(f"demo_{Color.RED}")
