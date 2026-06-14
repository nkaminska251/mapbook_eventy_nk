from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

import tkintermapview

from config import COLOR_BG, COLOR_BTN, COLOR_FRAME, COLOR_TEXT, DATABASE_FILE
from controller import EventController
from model import Employee, Event, EventCompany, Guest
from storage import Database


class EventManagerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("System Zarządzania Eventami")
        self.root.geometry("1250x760")
        self.root.configure(bg=COLOR_BG)

        database_path = Path(__file__).resolve().with_name(DATABASE_FILE)
        self.controller = EventController(Database(database_path))

        self.current_displayed_companies: list[EventCompany] = []
        self.current_displayed_events: list[Event] = []
        self.current_displayed_employees: list[Employee] = []
        self.current_displayed_guests: list[Guest] = []
        self.map_markers = []

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=COLOR_BTN, foreground=COLOR_TEXT, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", COLOR_FRAME)])

        self.show_login_screen()

    def show_login_screen(self) -> None:
        self.login_frame = tk.Frame(self.root, bg=COLOR_FRAME, bd=2, relief="groove")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=250)

        tk.Label(
            self.login_frame,
            text="Logowanie do systemu",
            font=("Arial", 14, "bold"),
            bg=COLOR_FRAME,
            fg=COLOR_TEXT,
        ).pack(pady=20)

        tk.Label(self.login_frame, text="Użytkownik:", bg=COLOR_FRAME, fg=COLOR_TEXT).pack()
        self.entry_username = tk.Entry(self.login_frame)
        self.entry_username.pack(pady=5)

        tk.Label(self.login_frame, text="Hasło:", bg=COLOR_FRAME, fg=COLOR_TEXT).pack()
        self.entry_password = tk.Entry(self.login_frame, show="*")
        self.entry_password.pack(pady=5)

        tk.Button(
            self.login_frame,
            text="Zaloguj się",
            command=self.check_login,
            bg=COLOR_BTN,
            fg=COLOR_TEXT,
        ).pack(pady=15)

    def check_login(self) -> None:
        if self.entry_username.get() == "admin" and self.entry_password.get() == "admin":
            self.login_frame.destroy()
            self.build_main_interface()
            return

        messagebox.showerror("Błąd", "Nieprawidłowy login lub hasło!")

    def build_main_interface(self) -> None:
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_companies = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_events = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_employees = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_guests = tk.Frame(self.notebook, bg=COLOR_BG)

        self.notebook.add(self.tab_companies, text="Firmy")
        self.notebook.add(self.tab_events, text="Wydarzenia")
        self.notebook.add(self.tab_employees, text="Pracownicy")
        self.notebook.add(self.tab_guests, text="Goście")

        self.map_frame = tk.Frame(self.root, bg=COLOR_FRAME)
        self.map_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.map_widget = tkintermapview.TkinterMapView(self.map_frame, width=1250, height=400, corner_radius=5)
        self.map_widget.set_position(52.2, 21.0)
        self.map_widget.set_zoom(6)
        self.map_widget.pack(fill="both", expand=True)

        self.setup_companies_tab()
        self.setup_events_tab()
        self.setup_employees_tab()
        self.setup_guests_tab()

        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.refresh_all_map_markers())

    def refresh_all_map_markers(self) -> None:
        for marker in self.map_markers:
            marker.delete()
        self.map_markers.clear()

        selected_tab_idx = self.notebook.index(self.notebook.select())
        grouped_locations = {}

        # ZAKŁADKA 0: FIRMY
        if selected_tab_idx == 0:
            for company in self.controller.database.companies:
                if company.coordinates and len(company.coordinates) == 2:
                    coords = (float(company.coordinates[0]), float(company.coordinates[1]))
                    grouped_locations.setdefault(coords, []).append(company.name)

        # ZAKŁADKA 1: WYDARZENIA
        elif selected_tab_idx == 1:
            for event in self.controller.database.events:
                if event.coordinates and len(event.coordinates) == 2:
                    coords = (float(event.coordinates[0]), float(event.coordinates[1]))
                    grouped_locations.setdefault(coords, []).append(event.name)

        # ZAKŁADKA 2: PRACOWNICY
        elif selected_tab_idx == 2:
            for employee in self.controller.database.employees:
                if employee.coordinates and len(employee.coordinates) == 2:
                    coords = (float(employee.coordinates[0]), float(employee.coordinates[1]))
                    text = f"{employee.name} {employee.surname} ({employee.event_name})"
                    grouped_locations.setdefault(coords, []).append(text)

        # ZAKŁADKA 3: GOŚCIE
        elif selected_tab_idx == 3:
            for guest in self.controller.database.guests:
                if guest.coordinates and len(guest.coordinates) == 2:
                    coords = (float(guest.coordinates[0]), float(guest.coordinates[1]))
                    text = f"{guest.name} {guest.surname} ({guest.event_name})"
                    grouped_locations.setdefault(coords, []).append(text)

        for coords, labels in grouped_locations.items():
            combined_text = "\n".join(labels)
            m = self.map_widget.set_marker(
                coords[0], coords[1],
                text=combined_text,
                marker_color_circle="#5c6bc0",  # Główny kolor znacznika
                marker_color_outside="#3f51b5",  # Kontrastowa, ciemniejsza obwódka znacznika
                text_color="#000000",  # Kolor czcionki - czarny
                font=("Arial", 8)  # Krój pisma Arial, mniejszy rozmiar
            )
            self.map_markers.append(m)

    # --- OKNO DO EDYCJI ---
    def open_edit_dialog(self, title: str, fields: list[str], current_values: list[str], callback) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.configure(bg=COLOR_FRAME)
        dialog.transient(self.root)
        dialog.grab_set()

        entries = {}
        for field, val in zip(fields, current_values):
            frame = tk.Frame(dialog, bg=COLOR_FRAME)
            frame.pack(fill="x", padx=20, pady=5)
            tk.Label(frame, text=f"{field}:", bg=COLOR_FRAME, fg=COLOR_TEXT, width=15, anchor="w").pack(side="left")
            entry = tk.Entry(frame)
            entry.insert(0, val)
            entry.pack(side="right", fill="x", expand=True)
            entries[field] = entry

        def on_save():
            updated_args = [entries[f].get() for f in fields]
            dialog.destroy()
            callback(*updated_args)

        btn_save = tk.Button(dialog, text="Zapisz zmiany", bg=COLOR_BTN, fg=COLOR_TEXT, command=on_save)
        btn_save.pack(pady=20)

    # --- ZAKŁADKA: FIRMY ---
    def setup_companies_tab(self) -> None:
        top_frame = tk.Frame(self.tab_companies, bg=COLOR_BG)
        top_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(top_frame, text="Szukaj:", bg=COLOR_BG, fg=COLOR_TEXT).pack(side="left", padx=5)
        self.entry_search_companies = tk.Entry(top_frame)
        self.entry_search_companies.pack(side="left", padx=5, fill="x", expand=True)
        self.entry_search_companies.bind("<KeyRelease>", lambda e: self.load_companies())

        btn_delete = tk.Button(top_frame, text="Usuń zaznaczone", bg=COLOR_BTN, fg=COLOR_TEXT,
                               command=self.delete_company)
        btn_delete.pack(side="right", padx=5)

        btn_edit = tk.Button(top_frame, text="Edytuj zaznaczone", bg=COLOR_BTN, fg=COLOR_TEXT,
                             command=self.edit_company)
        btn_edit.pack(side="right", padx=5)

        self.tree_companies = ttk.Treeview(self.tab_companies, columns=("name", "city"), show="headings")
        self.tree_companies.heading("name", text="Nazwa firma")
        self.tree_companies.heading("city", text="Adres / Miasto")
        self.tree_companies.pack(fill="both", expand=True, padx=10, pady=5)

        self.load_companies()

    def load_companies(self) -> None:
        for item in self.tree_companies.get_children():
            self.tree_companies.delete(item)
        search_text = self.entry_search_companies.get()
        self.current_displayed_companies = self.controller.filter_companies(search_text)
        for comp in self.current_displayed_companies:
            self.tree_companies.insert("", "end", values=(comp.name, comp.city))

    def delete_company(self) -> None:
        selected = self.tree_companies.selection()
        if not selected:
            messagebox.showwarning("Uwaga", "Wybierz firmę do usunięcia!")
            return
        idx = self.tree_companies.index(selected[0])
        company_to_remove = self.current_displayed_companies[idx]
        self.controller.remove_company(company_to_remove)
        self.load_companies()
        self.refresh_all_map_markers()

    def edit_company(self) -> None:
        selected = self.tree_companies.selection()
        if not selected:
            messagebox.showwarning("Uwaga", "Wybierz firmę do edycji!")
            return
        idx = self.tree_companies.index(selected[0])
        company = self.current_displayed_companies[idx]

        def save_callback(name, city):
            self.controller.update_company(company, name, city)
            self.load_companies()
            self.refresh_all_map_markers()

        self.open_edit_dialog("Edycja Firmy", ["Nazwa", "Adres / Miasto"], [company.name, company.city], save_callback)

    # --- ZAKŁADKA: WYDARZENIA ---
    def setup_events_tab(self) -> None:
        top_frame = tk.Frame(self.tab_events, bg=COLOR_BG)
        top_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(top_frame, text="Szukaj:", bg=COLOR_BG, fg=COLOR_TEXT).pack(side="left", padx=5)
        self.entry_search_events = tk.Entry(top_frame)
        self.entry_search_events.pack(side="left", padx=5, fill="x", expand=True)
        self.entry_search_events.bind("<KeyRelease>", lambda e: self.load_events())

        btn_delete = tk.Button(top_frame, text="Usuń zaznaczone", bg=COLOR_BTN, fg=COLOR_TEXT,
                               command=self.delete_event)
        btn_delete.pack(side="right", padx=5)

        btn_edit = tk.Button(top_frame, text="Edytuj zaznaczone", bg=COLOR_BTN, fg=COLOR_TEXT, command=self.edit_event)
        btn_edit.pack(side="right", padx=5)

        self.tree_events = ttk.Treeview(self.tab_events, columns=("name", "city", "company"), show="headings")
        self.tree_events.heading("name", text="Nazwa wydarzenia")
        self.tree_events.heading("city", text="Lokalizacja")
        self.tree_events.heading("company", text="Organizacja")
        self.tree_events.pack(fill="both", expand=True, padx=10, pady=5)

        self.load_events()

    def load_events(self) -> None:
        for item in self.tree_events.get_children():
            self.tree_events.delete(item)
        search_text = self.entry_search_events.get()
        self.current_displayed_events = self.controller.filter_events(search_text)
        for ev in self.current_displayed_events:
            self.tree_events.insert("", "end", values=(ev.name, ev.city, ev.company_name))

    def delete_event(self) -> None:
        selected = self.tree_events.selection()
        if not selected:
            messagebox.showwarning("Uwaga", "Wybierz wydarzenie do usunięcia!")
            return
        idx = self.tree_events.index(selected[0])
        event_to_remove = self.current_displayed_events[idx]
        self.controller.remove_event(event_to_remove)
        self.load_events()
        self.refresh_all_map_markers()

    def edit_event(self) -> None:
        selected = self.tree_events.selection()
        if not selected:
            messagebox.showwarning("Uwaga", "Wybierz wydarzenie do edycji!")
            return
        idx = self.tree_events.index(selected[0])
        event = self.current_displayed_events[idx]

        def save_callback(name, city, company_name):
            self.controller.update_event(event, name, city, company_name)
            self.load_events()
            self.refresh_all_map_markers()

        self.open_edit_dialog("Edycja Wydarzenia", ["Nazwa", "Lokalizacja", "Organizacja"],
                              [event.name, event.city, event.company_name], save_callback)

    # --- ZAKŁADKA: PRACOWNICY ---
    def setup_employees_tab(self) -> None:
        top_frame = tk.Frame(self.tab_employees, bg=COLOR_BG)
        top_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(top_frame, text="Szukaj:", bg=COLOR_BG, fg=COLOR_TEXT).pack(side="left", padx=5)
        self.entry_search_employees = tk.Entry(top_frame)
        self.entry_search_employees.pack(side="left", padx=5, fill="x", expand=True)
        self.entry_search_employees.bind("<KeyRelease>", lambda e: self.load_employees())

        btn_delete = tk.Button(top_frame, text="Usuń zaznaczone", bg=COLOR_BTN, fg=COLOR_TEXT,
                               command=self.delete_employee)
        btn_delete.pack(side="right", padx=5)

        btn_edit = tk.Button(top_frame, text="Edytuj zaznaczone", bg=COLOR_BTN, fg=COLOR_TEXT,
                             command=self.edit_employee)
        btn_edit.pack(side="right", padx=5)

        self.tree_employees = ttk.Treeview(self.tab_employees, columns=("name", "surname", "city", "event"),
                                           show="headings")
        self.tree_employees.heading("name", text="Imię")
        self.tree_employees.heading("surname", text="Nazwisko")
        self.tree_employees.heading("city", text="Adres zamieszkania")
        self.tree_employees.heading("event", text="Przypisany event")
        self.tree_employees.pack(fill="both", expand=True, padx=10, pady=5)

        self.load_employees()

    def load_employees(self) -> None:
        for item in self.tree_employees.get_children():
            self.tree_employees.delete(item)
        search_text = self.entry_search_employees.get()
        self.current_displayed_employees = self.controller.filter_employees(search_text)
        for emp in self.current_displayed_employees:
            self.tree_employees.insert("", "end", values=(emp.name, emp.surname, emp.city, emp.event_name))

    def delete_employee(self) -> None:
        selected = self.tree_employees.selection()
        if not selected:
            messagebox.showwarning("Uwaga", "Wybierz pracownika do usunięcia!")
            return
        idx = self.tree_employees.index(selected[0])
        emp_to_remove = self.current_displayed_employees[idx]
        self.controller.remove_employee(emp_to_remove)
        self.load_employees()
        self.refresh_all_map_markers()

    def edit_employee(self) -> None:
        selected = self.tree_employees.selection()
        if not selected:
            messagebox.showwarning("Uwaga", "Wybierz pracownika do edycji!")
            return
        idx = self.tree_employees.index(selected[0])
        emp = self.current_displayed_employees[idx]

        def save_callback(name, surname, city, event_name):
            self.controller.update_employee(emp, name, surname, city, event_name)
            self.load_employees()
            self.refresh_all_map_markers()

        self.open_edit_dialog("Edycja Pracownika", ["Imię", "Nazwisko", "Adres", "Przypisany event"],
                              [emp.name, emp.surname, emp.city, emp.event_name], save_callback)

    # --- ZAKŁADKA: GOŚCIE ---
    def setup_guests_tab(self) -> None:
        top_frame = tk.Frame(self.tab_guests, bg=COLOR_BG)
        top_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(top_frame, text="Szukaj:", bg=COLOR_BG, fg=COLOR_TEXT).pack(side="left", padx=5)
        self.entry_search_guests = tk.Entry(top_frame)
        self.entry_search_guests.pack(side="left", padx=5, fill="x", expand=True)
        self.entry_search_guests.bind("<KeyRelease>", lambda e: self.load_guests())

        btn_delete = tk.Button(top_frame, text="Usuń zaznaczone", bg=COLOR_BTN, fg=COLOR_TEXT,
                               command=self.delete_guest)
        btn_delete.pack(side="right", padx=5)

        btn_edit = tk.Button(top_frame, text="Edytuj zaznaczone", bg=COLOR_BTN, fg=COLOR_TEXT, command=self.edit_guest)
        btn_edit.pack(side="right", padx=5)

        self.tree_guests = ttk.Treeview(self.tab_guests, columns=("name", "surname", "city", "event"), show="headings")
        self.tree_guests.heading("name", text="Imię")
        self.tree_guests.heading("surname", text="Nazwisko")
        self.tree_guests.heading("city", text="Miejscowość")
        self.tree_guests.heading("event", text="Wydarzenie")
        self.tree_guests.pack(fill="both", expand=True, padx=10, pady=5)

        self.load_guests()

    def load_guests(self) -> None:
        for item in self.tree_guests.get_children():
            self.tree_guests.delete(item)
        search_text = self.entry_search_guests.get()
        self.current_displayed_guests = self.controller.filter_guests(search_text)
        for gst in self.current_displayed_guests:
            self.tree_guests.insert("", "end", values=(gst.name, gst.surname, gst.city, gst.event_name))

    def delete_guest(self) -> None:
        selected = self.tree_guests.selection()
        if not selected:
            messagebox.showwarning("Uwaga", "Wybierz gościa do usunięcia!")
            return
        idx = self.tree_guests.index(selected[0])
        gst_to_remove = self.current_displayed_guests[idx]
        self.controller.remove_guest(gst_to_remove)
        self.load_guests()
        self.refresh_all_map_markers()

    def edit_guest(self) -> None:
        selected = self.tree_guests.selection()
        if not selected:
            messagebox.showwarning("Uwaga", "Wybierz gościa do edycji!")
            return
        idx = self.tree_guests.index(selected[0])
        guest = self.current_displayed_guests[idx]

        def save_callback(name, surname, city, event_name):
            self.controller.update_guest(guest, name, surname, city, event_name)
            self.load_guests()
            self.refresh_all_map_markers()

        self.open_edit_dialog("Edycja Gościa", ["Imię", "Nazwisko", "Miejscowość", "Wydarzenie"],
                              [guest.name, guest.surname, guest.city, guest.event_name], save_callback)


if __name__ == "__main__":
    root = tk.Tk()
    app = EventManagerApp(root)
    root.mainloop()
