#model of the app
from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class BaseMapObject:
    name: str
    city: str
    coordinates: list[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EventCompany(BaseMapObject):
    pass


@dataclass
class Event(BaseMapObject):
    company_name: str = ""


@dataclass
class Person:
    name: str
    surname: str
    city: str
    event_name: str
    coordinates: list[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Employee(Person):
    pass


@dataclass
class Guest(Person):
    pass