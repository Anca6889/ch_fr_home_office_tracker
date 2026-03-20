# -*- coding: utf-8 -*-
"""
Persistence layer — UserManager (user list) and DataStore (per-user day data).
"""

import json
from pathlib import Path

from constants import CATEGORIES

DATA_DIR   = Path(__file__).parent
USERS_FILE = DATA_DIR / "home_office_users.json"


def _user_data_file(username: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in username)
    return DATA_DIR / f"home_office_{safe}.json"


# ── User Manager ──────────────────────────────────────────────────────────────

class UserManager:
    """Persists the list of users and which one is currently active."""

    def __init__(self):
        self._users:   list = []
        self._current: str  = ""
        self._load()

    def _load(self):
        if USERS_FILE.exists():
            try:
                data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
                self._users   = data.get("users", [])
                self._current = data.get("current", "")
            except Exception:
                pass
        if not self._users:
            self._users   = ["Default"]
            self._current = "Default"
            self._save()
        if self._current not in self._users:
            self._current = self._users[0]

    def _save(self):
        USERS_FILE.write_text(
            json.dumps({"users": self._users, "current": self._current},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @property
    def users(self) -> list:
        return list(self._users)

    @property
    def current(self) -> str:
        return self._current

    def set_current(self, name: str):
        if name in self._users:
            self._current = name
            self._save()

    def add_user(self, name: str) -> bool:
        name = name.strip()
        if name and name not in self._users:
            self._users.append(name)
            self._save()
            return True
        return False

    def delete_user(self, name: str) -> bool:
        if name in self._users and len(self._users) > 1:
            self._users.remove(name)
            if self._current == name:
                self._current = self._users[0]
            self._save()
            return True
        return False


# ── Data Store ────────────────────────────────────────────────────────────────

class DataStore:
    """Per-user JSON persistence.
    Schema: {"2025": {"3": {"15": "maison", ...}, ...}, ...}
    """

    def __init__(self, username: str):
        self._username = username
        self._file     = _user_data_file(username)
        self._data: dict = {}
        self.load()

    def load(self):
        if self._file.exists():
            try:
                self._data = json.loads(self._file.read_text(encoding="utf-8"))
            except Exception:
                self._data = {}

    def save(self):
        self._file.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get(self, year: int, month: int, day: int):
        return self._data.get(str(year), {}).get(str(month), {}).get(str(day))

    def set(self, year: int, month: int, day: int, category):
        y, m, d = str(year), str(month), str(day)
        if category is None:
            self._data.get(y, {}).get(m, {}).pop(d, None)
        else:
            self._data.setdefault(y, {}).setdefault(m, {})[d] = category
        self.save()

    def year_counts(self, year: int) -> dict:
        counts = {k: 0 for k, *_ in CATEGORIES}
        for month_data in self._data.get(str(year), {}).values():
            for cat in month_data.values():
                if cat in counts:
                    counts[cat] += 1
        return counts

    def month_days(self, year: int, month: int) -> dict:
        return dict(self._data.get(str(year), {}).get(str(month), {}))
