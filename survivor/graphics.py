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


@dataclass
class Circle:
    x: float
    y: float
    radius: float
    color: str
    type: str = "circle"


@dataclass
class Triangle:
    x: float
    y: float
    size: float
    angle: float
    color: str
    type: str = "triangle"


@dataclass
class Cross:
    x: float
    y: float
    size: float
    color: str
    type: str = "cross"


class Frame:
    def __init__(self) -> None:
        self.objects = []

    def add_sphere(self, sphere):
        self.objects.append(sphere)

    def add_rectangle(self, rect):
        self.objects.append(rect)

    def add_text(self, text):
        self.objects.append(text)

    def add_circle(self, circle: Circle):
        self.objects.append(circle)

    def add_triangle(self, triangle: Triangle):
        self.objects.append(triangle)

    def add_cross(self, cross: Cross):
        self.objects.append(cross)

    def serialize(self):
        serialized_objects = [vars(obj) for obj in self.objects]
        return json.dumps(serialized_objects)
