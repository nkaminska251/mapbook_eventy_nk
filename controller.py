from __future__ import annotations

from map_service import get_coordinates
from model import Employee, Event, EventCompany, Guest
from storage import Database


class EventController:
    def __init__(self, database: Database):
        self.database = database

    # --- FIRMY ---
    def add_company(self, name: str, city: str) -> None:
        self.database.companies.append(EventCompany(name=name, city=city, coordinates=get_coordinates(city)))
        self.database.save()

    def update_company(self, original_company: EventCompany, name: str, city: str) -> None:
        if original_company in self.database.companies:
            idx = self.database.companies.index(original_company)
            self.database.companies[idx] = EventCompany(name=name, city=city, coordinates=get_coordinates(city))
            self.database.save()

    def remove_company(self, company: EventCompany) -> None:
        if company in self.database.companies:
            self.database.companies.remove(company)
            self.database.save()

    def filter_companies(self, text: str = "") -> list[EventCompany]:
        text = text.lower().strip()
        return [
            company for company in self.database.companies
            if not text or text in company.name.lower() or text in company.city.lower()
        ]

    # --- WYDARZENIA ---
    def add_event(self, name: str, city: str, company_name: str) -> None:
        self.database.events.append(
            Event(name=name, city=city, company_name=company_name, coordinates=get_coordinates(city))
        )
        self.database.save()

    def update_event(self, original_event: Event, name: str, city: str, company_name: str) -> None:
        if original_event in self.database.events:
            idx = self.database.events.index(original_event)
            self.database.events[idx] = Event(
                name=name,
                city=city,
                company_name=company_name,
                coordinates=get_coordinates(city),
            )
            self.database.save()

    def remove_event(self, event: Event) -> None:
        if event in self.database.events:
            self.database.events.remove(event)
            self.database.save()

    def filter_events(self, text: str = "", company_name: str = "") -> list[Event]:
        text = text.lower().strip()
        return [
            event for event in self.database.events
            if (not text or text in event.name.lower() or text in event.city.lower())
            and (not company_name or event.company_name == company_name)
        ]

    # --- PRACOWNICY ---
    def add_employee(self, name: str, surname: str, city: str, event_name: str) -> None:
        self.database.employees.append(
            Employee(name=name, surname=surname, city=city, event_name=event_name, coordinates=get_coordinates(city))
        )
        self.database.save()

    def update_employee(self, original_employee: Employee, name: str, surname: str, city: str, event_name: str) -> None:
        if original_employee in self.database.employees:
            idx = self.database.employees.index(original_employee)
            self.database.employees[idx] = Employee(
                name=name,
                surname=surname,
                city=city,
                event_name=event_name,
                coordinates=get_coordinates(city),
            )
            self.database.save()

    def remove_employee(self, employee: Employee) -> None:
        if employee in self.database.employees:
            self.database.employees.remove(employee)
            self.database.save()

    def filter_employees(self, text: str = "", event_name: str = "") -> list[Employee]:
        text = text.lower().strip()
        return [
            employee for employee in self.database.employees
            if (
                not text
                or text in employee.name.lower()
                or text in employee.surname.lower()
                or text in employee.city.lower()
            )
            and (not event_name or employee.event_name == event_name)
        ]

    # --- GOŚCIE ---
    def add_guest(self, name: str, surname: str, city: str, event_name: str) -> None:
        self.database.guests.append(
            Guest(name=name, surname=surname, city=city, event_name=event_name, coordinates=get_coordinates(city))
        )
        self.database.save()

    def update_guest(self, original_guest: Guest, name: str, surname: str, city: str, event_name: str) -> None:
        if original_guest in self.database.guests:
            idx = self.database.guests.index(original_guest)
            self.database.guests[idx] = Guest(
                name=name,
                surname=surname,
                city=city,
                event_name=event_name,
                coordinates=get_coordinates(city),
            )
            self.database.save()

    def remove_guest(self, guest: Guest) -> None:
        if guest in self.database.guests:
            self.database.guests.remove(guest)
            self.database.save()

    def filter_guests(self, text: str = "", event_name: str = "") -> list[Guest]:
        text = text.lower().strip()
        return [
            guest for guest in self.database.guests
            if (
                not text
                or text in guest.name.lower()
                or text in guest.surname.lower()
                or text in guest.city.lower()
            )
            and (not event_name or guest.event_name == event_name)
        ]