from dataclasses import dataclass
import json


@dataclass
class Text:
    x: float
    y: float
    text: str
    color: str
    font_size: int = 20
    type: str = "text"


@dataclass
class Sphere:
    x: float
    y: float
    radius: float
    color: str
    vx: float = 0
    vy: float = 0
    type: str = "sphere"


@dataclass
class Rectangle:
    x: float
    y: float
    width: float
    height: float
    color: str
    vx: float = 0
    vy: float = 0
    type: str = "rectangle"


class Frame:
    def __init__(self) -> None:
        self.objects = []

    def add_sphere(self, sphere):
        self.objects.append(sphere)

    def add_rectangle(self, rect):
        self.objects.append(rect)

    def add_text(self, text):
        self.objects.append(text)

    def serialize(self):
        serialized_objects = [vars(obj) for obj in self.objects]
        return json.dumps(serialized_objects)
