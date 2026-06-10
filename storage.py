from __future__ import annotations

import json
from pathlib import Path

from map_service import get_coordinates
from model import Employee, Event, EventCompany, Guest


class Database:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.companies: list[EventCompany] = []
        self.events: list[Event] = []
        self.employees: list[Employee] = []
        self.guests: list[Guest] = []
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.save()
            return

        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.companies = [EventCompany(**item) for item in data.get("companies", [])]
        self.events = [Event(**item) for item in data.get("events", [])]
        self.employees = [Employee(**item) for item in data.get("employees", [])]
        self.guests = [Guest(**item) for item in data.get("guests", [])]
        self.fill_missing_coordinates()

    def fill_missing_coordinates(self) -> None:
        changed = False
        all_items = [*self.companies, *self.events, *self.employees, *self.guests]

        for item in all_items:
            if item.coordinates:
                continue

            coordinates = get_coordinates(item.city)
            if coordinates:
                item.coordinates = coordinates
                changed = True

        if changed:
            self.save()

    def save(self) -> None:
        data = {
            "companies": [company.to_dict() for company in self.companies],
            "events": [event.to_dict() for event in self.events],
            "employees": [employee.to_dict() for employee in self.employees],
            "guests": [guest.to_dict() for guest in self.guests],
        }

        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)