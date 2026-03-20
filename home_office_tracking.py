#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Home Office Tracking — Work-day tracking
Franco-Swiss Agreement of April 11, 1983 (remote work)

Run with:
    py home_office_tracking.py
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

from constants import T
from data import UserManager, DataStore, _user_data_file
from widgets import CalendarWidget, SidePanel, _apply_dark_ttk
from pdf_export import export_pdf


# ── Application Shell ─────────────────────────────────────────────────────────

class HomeOfficeApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Home Office Tracking — Franco-Swiss Agreement, April 11, 1983")
        self.geometry("1280x720")
        self.minsize(1060, 600)
        self.configure(bg=T["bg"])

        _apply_dark_ttk(self)

        self._users = UserManager()
        self._store = DataStore(self._users.current)
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Top bar ──────────────────────────────────────────────────────────
        top = tk.Frame(self, bg=T["bg_panel"], height=46)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="  Home Office Tracking",
                 font=("Segoe UI", 13, "bold"),
                 bg=T["bg_panel"], fg=T["accent"]).pack(side="left", padx=4)

        tk.Label(top, text="Remote work tracking — Franco-Swiss Agreement, April 11, 1983",
                 font=("Segoe UI", 9),
                 bg=T["bg_panel"], fg=T["fg_dim"]).pack(side="left", padx=8)

        # Export PDF button (far right)
        tk.Button(top, text="⬇ Export PDF", command=self._export_pdf,
                  bg="#2C4A7C", fg="#7EB8F0",
                  relief="flat", bd=0,
                  activebackground=T["accent"], activeforeground=T["bg"],
                  font=("Segoe UI", 9, "bold"), padx=10, pady=0,
                  cursor="hand2").pack(side="right", padx=12, pady=8)

        # User section (right of top bar, left of Export button)
        user_frame = tk.Frame(top, bg=T["bg_panel"])
        user_frame.pack(side="right", padx=(0, 6), pady=6)

        tk.Label(user_frame, text="User:", bg=T["bg_panel"], fg=T["fg_dim"],
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 4))

        self._user_var = tk.StringVar(value=self._users.current)
        self._user_cb  = ttk.Combobox(
            user_frame, textvariable=self._user_var,
            values=self._users.users, width=14, state="readonly",
            font=("Segoe UI", 9),
        )
        self._user_cb.pack(side="left")
        self._user_cb.bind("<<ComboboxSelected>>", self._on_user_select)

        tk.Button(user_frame, text="+", command=self._add_user,
                  bg=T["bg_cell"], fg=T["ok"],
                  relief="flat", bd=0,
                  activebackground=T["ok"], activeforeground=T["bg"],
                  font=("Segoe UI", 10, "bold"), padx=6, pady=0,
                  cursor="hand2").pack(side="left", padx=(4, 2))

        tk.Button(user_frame, text="✕", command=self._delete_user,
                  bg=T["bg_cell"], fg=T["danger"],
                  relief="flat", bd=0,
                  activebackground=T["danger"], activeforeground=T["bg"],
                  font=("Segoe UI", 9), padx=6, pady=0,
                  cursor="hand2").pack(side="left")

        # ── Legend bar (bottom) ───────────────────────────────────────────────
        legend = self._build_legend()
        legend.pack(side="bottom", fill="x")

        # ── Main content ──────────────────────────────────────────────────────
        main = tk.Frame(self, bg=T["bg"])
        main.pack(fill="both", expand=True)

        self._panel = SidePanel(main, self._store)
        self._panel.pack(side="right", fill="y")

        tk.Frame(main, bg=T["separator"], width=1).pack(side="right", fill="y")

        self._cal = CalendarWidget(main, self._store, on_change=self._refresh)
        self._cal.pack(side="left", fill="both", expand=True)

        self._refresh()

    def _build_legend(self):
        from constants import CATEGORIES
        bar = tk.Frame(self, bg=T["bg_panel"], pady=5)
        tk.Label(bar, text="  Left click: assign   Right click: clear",
                 font=("Segoe UI", 8, "italic"),
                 bg=T["bg_panel"], fg=T["fg_dim"]).pack(side="left", padx=6)
        for code, label, color in CATEGORIES:
            f = tk.Frame(bar, bg=T["bg_panel"])
            f.pack(side="left", padx=8)
            tk.Label(f, text="■", fg=color, bg=T["bg_panel"],
                     font=("Segoe UI", 11)).pack(side="left")
            tk.Label(f, text=label, fg=T["fg_dim"], bg=T["bg_panel"],
                     font=("Segoe UI", 8)).pack(side="left", padx=2)
        return bar

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _refresh(self):
        self._panel.update(self._cal.current_year)

    def _export_pdf(self):
        export_pdf(self._store, self._cal.current_year,
                   self._users.current, self)

    def _on_user_select(self, _=None):
        name = self._user_var.get()
        self._users.set_current(name)
        self._store = DataStore(name)
        self._cal.set_store(self._store)
        self._panel.set_store(self._store)
        self._refresh()

    def _add_user(self):
        name = simpledialog.askstring(
            "Add user", "Enter the new user's name:",
            parent=self,
        )
        if not name:
            return
        if not self._users.add_user(name):
            messagebox.showwarning("Already exists",
                                   f'User "{name}" already exists.', parent=self)
            return
        self._user_cb.configure(values=self._users.users)
        # Switch to the new user immediately
        self._user_var.set(name)
        self._on_user_select()

    def _delete_user(self):
        name = self._users.current
        if len(self._users.users) == 1:
            messagebox.showwarning("Cannot delete",
                                   "At least one user must remain.", parent=self)
            return
        if not messagebox.askyesno("Delete user",
                                   f'Delete user "{name}" and all their data?\n\nThis cannot be undone.',
                                   parent=self):
            return
        # Optionally remove the data file
        data_file = _user_data_file(name)
        if data_file.exists():
            data_file.unlink()
        self._users.delete_user(name)
        self._user_cb.configure(values=self._users.users)
        self._user_var.set(self._users.current)
        self._on_user_select()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = HomeOfficeApp()
    app.mainloop()
