# -*- coding: utf-8 -*-
"""
UI widgets — CalendarWidget, SidePanel, and tkinter/ttk helpers.
"""

import calendar
import datetime
import tkinter as tk
from tkinter import ttk

from constants import (
    T, CATEGORIES, MONTHS_EN, DAYS_EN,
    CAT_BUREAU, CAT_MAISON, CAT_EN_FR, CAT_HORS_FR, CAT_NON_RETOUR, CAT_CONGE,
    CAT_COLOR, MAX_HORS_FR_EXCHANGE,
)
from data import DataStore
from engine import compute_status


# ── Calendar Widget ───────────────────────────────────────────────────────────

class CalendarWidget(tk.Frame):
    """Monthly calendar grid with click-to-categorize."""

    def __init__(self, parent, store: DataStore, on_change):
        super().__init__(parent, bg=T["bg"])
        self._store     = store
        self._on_change = on_change
        self._popup     = None

        today = datetime.date.today()
        self._year  = today.year
        self._month = today.month
        self._today = today

        self._build_nav()
        self._build_headers()
        self._grid_frame = tk.Frame(self, bg=T["bg"])
        self._grid_frame.pack(fill="both", expand=True, padx=6, pady=4)
        self.refresh()

    def set_store(self, store: DataStore):
        self._store = store
        self.refresh()

    # ── Nav bar ───────────────────────────────────────────────────────────────

    def _build_nav(self):
        bar = tk.Frame(self, bg=T["bg"])
        bar.pack(fill="x", padx=8, pady=(8, 2))

        tk.Button(bar, text="◀", command=self._prev_month, **_btn_kw()).pack(side="left", padx=(0, 4))
        tk.Button(bar, text="▶", command=self._next_month, **_btn_kw()).pack(side="right", padx=(4, 0))

        center = tk.Frame(bar, bg=T["bg"])
        center.pack(side="left", expand=True)

        self._month_var = tk.StringVar()
        self._month_cb  = ttk.Combobox(
            center, textvariable=self._month_var,
            values=MONTHS_EN, width=11, state="readonly",
            font=("Segoe UI", 11, "bold"),
        )
        self._month_cb.pack(side="left", padx=4)
        self._month_cb.bind("<<ComboboxSelected>>", self._on_month_select)

        self._year_var = tk.StringVar()
        self._year_cb  = ttk.Combobox(
            center, textvariable=self._year_var,
            values=[str(y) for y in range(2020, 2036)],
            width=6, state="readonly",
            font=("Segoe UI", 11),
        )
        self._year_cb.pack(side="left", padx=4)
        self._year_cb.bind("<<ComboboxSelected>>", self._on_year_select)

        tk.Button(bar, text="Today", command=self._go_today, **_btn_kw()).pack(side="right", padx=(0, 8))

        self._sync_combos()

    def _build_headers(self):
        hdr = tk.Frame(self, bg=T["bg"])
        hdr.pack(fill="x", padx=6, pady=(2, 0))
        for i, name in enumerate(DAYS_EN):
            fg = T["fg_dim"] if i >= 5 else T["fg"]
            tk.Label(
                hdr, text=name, fg=fg, bg=T["bg"],
                font=("Segoe UI", 9, "bold"), anchor="center",
            ).grid(row=0, column=i, padx=2, pady=2, sticky="ew")
            hdr.columnconfigure(i, weight=1, uniform="dayhdr")

    # ── Grid rendering ────────────────────────────────────────────────────────

    def refresh(self):
        for w in self._grid_frame.winfo_children():
            w.destroy()

        cal = calendar.monthcalendar(self._year, self._month)
        while len(cal) < 6:
            cal.append([0] * 7)

        for row_i, week in enumerate(cal):
            self._grid_frame.rowconfigure(row_i, weight=1, uniform="calrow")
            for col_i, day_num in enumerate(week):
                self._grid_frame.columnconfigure(col_i, weight=1, uniform="calcol")
                cell = self._make_cell(day_num, col_i)
                cell.grid(row=row_i, column=col_i, padx=2, pady=2, sticky="nsew")

    def _make_cell(self, day_num: int, col_i: int) -> tk.Frame:
        is_weekend = col_i >= 5
        is_today   = (
            day_num > 0 and
            self._year  == self._today.year and
            self._month == self._today.month and
            day_num     == self._today.day
        )

        cell = tk.Frame(self._grid_frame, bd=0, relief="flat")

        if day_num == 0:
            cell.configure(bg=T["bg"])
            return cell

        cat = self._store.get(self._year, self._month, day_num)

        _CAT_SHORT = {
            CAT_BUREAU:     "Office",
            CAT_MAISON:     "Home",
            CAT_EN_FR:      "FR",
            CAT_HORS_FR:    "Ext",
            CAT_NON_RETOUR: "NRR",
            CAT_CONGE:      "Vac",
        }

        if cat:
            bg, fg = CAT_COLOR[cat], "#FFFFFF"
            cat_text = _CAT_SHORT[cat]
        elif is_today:
            bg, fg = T["bg_today"], T["accent"]
            cat_text = ""
        elif is_weekend:
            bg, fg = T["bg_cell_wk"], T["fg_dim"]
            cat_text = ""
        else:
            bg, fg = T["bg_cell"], T["fg"]
            cat_text = ""

        cell.configure(bg=bg)
        cell.pack_propagate(False)

        if is_today:
            cell.configure(highlightbackground=T["accent"],
                           highlightcolor=T["accent"],
                           highlightthickness=2)

        num_lbl = tk.Label(
            cell, text=str(day_num),
            bg=bg, fg=fg,
            font=("Segoe UI", 11, "bold"),
            anchor="nw", padx=4, pady=2,
        )
        num_lbl.pack(fill="x")

        cat_lbl = tk.Label(
            cell, text=cat_text,
            bg=bg, fg="#DDDDDD" if cat else T["fg_dim"],
            font=("Segoe UI", 7),
            anchor="center",
        )
        cat_lbl.pack(expand=True, fill="both")

        cursor = "arrow" if is_weekend else "hand2"
        for widget in (cell, num_lbl, cat_lbl):
            widget.configure(cursor=cursor)
            widget.bind("<Button-3>", lambda e, d=day_num: self._right_click(d))
            if not is_weekend:
                widget.bind("<Button-1>", lambda e, d=day_num: self._left_click(e, d))
        return cell

    # ── Event handlers ────────────────────────────────────────────────────────

    def _left_click(self, event, day_num: int):
        if self._popup:
            try:
                self._popup.destroy()
            except Exception:
                pass
        self._popup = None

        current = self._store.get(self._year, self._month, day_num)
        menu = tk.Menu(
            self, tearoff=0,
            bg=T["bg_panel"], fg=T["fg"],
            activebackground=T["accent"], activeforeground=T["bg"],
            font=("Segoe UI", 10), bd=0,
        )
        for code, label, color in CATEGORIES:
            prefix = "✓ " if code == current else "   "
            menu.add_command(
                label=f"{prefix}{label}",
                command=lambda c=code, d=day_num: self._set_day(d, c),
            )
        menu.add_separator()
        menu.add_command(label="   Clear", command=lambda d=day_num: self._set_day(d, None))
        self._popup = menu
        menu.tk_popup(event.x_root, event.y_root)

    def _right_click(self, day_num: int):
        self._set_day(day_num, None)

    def _set_day(self, day_num: int, category):
        self._store.set(self._year, self._month, day_num, category)
        self.refresh()
        self._on_change()

    # ── Navigation ────────────────────────────────────────────────────────────

    def _prev_month(self):
        if self._month == 1:
            self._month, self._year = 12, self._year - 1
        else:
            self._month -= 1
        self._sync_combos(); self.refresh(); self._on_change()

    def _next_month(self):
        if self._month == 12:
            self._month, self._year = 1, self._year + 1
        else:
            self._month += 1
        self._sync_combos(); self.refresh(); self._on_change()

    def _go_today(self):
        t = datetime.date.today()
        self._year, self._month = t.year, t.month
        self._sync_combos(); self.refresh(); self._on_change()

    def _on_month_select(self, _=None):
        self._month = MONTHS_EN.index(self._month_var.get()) + 1
        self.refresh(); self._on_change()

    def _on_year_select(self, _=None):
        self._year = int(self._year_var.get())
        self.refresh(); self._on_change()

    def _sync_combos(self):
        self._month_var.set(MONTHS_EN[self._month - 1])
        self._year_var.set(str(self._year))

    @property
    def current_year(self):
        return self._year


# ── Side Panel ────────────────────────────────────────────────────────────────

class SidePanel(tk.Frame):
    """Yearly stats, quota progress, and alert banner."""

    def __init__(self, parent, store: DataStore):
        super().__init__(parent, bg=T["bg_panel"], width=420)
        self.pack_propagate(False)
        self._store    = store
        self._children = []

    def set_store(self, store: DataStore):
        self._store = store

    def update(self, year: int):
        for w in self._children:
            try:
                w.destroy()
            except Exception:
                pass
        self._children.clear()
        counts = self._store.year_counts(year)
        result = compute_status(counts)
        self._draw(year, counts, result)

    def _draw(self, year, counts, result):
        self._add_title(year)
        self._add_sep()
        self._add_alert(result)
        self._add_sep()
        self._add_progress(result)
        self._add_sep()
        self._add_counts(counts)
        self._add_sep()
        self._add_detail_metrics(result)

    def _keep(self, w):
        self._children.append(w)
        return w

    def _add_title(self, year):
        f = tk.Frame(self, bg=T["bg_panel"])
        f.pack(fill="x", padx=14, pady=(14, 4))
        self._keep(f)
        tk.Label(f, text="Summary", font=("Segoe UI", 13, "bold"),
                 bg=T["bg_panel"], fg=T["accent"]).pack(side="left")
        tk.Label(f, text=str(year), font=("Segoe UI", 13),
                 bg=T["bg_panel"], fg=T["fg_dim"]).pack(side="right")

    def _add_sep(self):
        sep = tk.Frame(self, bg=T["separator"], height=1)
        sep.pack(fill="x", padx=10, pady=5)
        self._keep(sep)

    def _add_alert(self, result):
        status = result["status"]
        bg = T["status_ok_bg"] if status == "ok" else T["status_danger_bg"]
        fg = T["ok"]           if status == "ok" else T["danger"]
        banner = tk.Label(
            self, text=result["status_reason"],
            bg=bg, fg=fg,
            font=("Segoe UI", 9, "bold"),
            wraplength=380, justify="center",
            pady=10, padx=10,
        )
        banner.pack(fill="x", padx=10, pady=4)
        self._keep(banner)

    def _add_progress(self, result):
        pct    = result["telework_pct"]
        rem    = result["remaining_telework_days"]
        max_tw = result["max_telework_days"]
        actual = result["actual_days"]
        color  = T["ok"] if result["status"] == "ok" else T["danger"]

        frame = tk.Frame(self, bg=T["bg_panel"])
        frame.pack(fill="x", padx=14, pady=(2, 6))
        self._keep(frame)

        tk.Label(frame, text=f"{pct:.1f}%",
                 font=("Segoe UI", 30, "bold"),
                 bg=T["bg_panel"], fg=color).pack(anchor="center")

        tk.Label(frame,
                 text=f"remote work  (limit: 40% of {actual} working days = {max_tw} days)",
                 font=("Segoe UI", 8),
                 bg=T["bg_panel"], fg=T["fg_dim"]).pack(anchor="center")

        canvas = tk.Canvas(frame, height=16, bg=T["bg_cell"], highlightthickness=0)
        canvas.pack(fill="x", pady=(6, 2))

        def draw_bar(c=canvas, col=color, p=pct, mt=max_tw, r=rem):
            c.update_idletasks()
            w = c.winfo_width() or 340
            c.delete("all")
            c.create_rectangle(0, 0, w, 16, fill=T["bg_cell"], outline="")
            fill_w = min(w, int(w * p / 100))
            if fill_w > 0:
                c.create_rectangle(0, 0, fill_w, 16, fill=col, outline="")
            marker = int(w * 0.40)
            c.create_line(marker, 0, marker, 16, fill=T["danger"], width=2, dash=(4, 2))
            c.create_text(w // 2, 8,
                          text=f"{mt - max(0, r)} / {mt} days",
                          fill="white" if p > 20 else T["fg"], font=("Segoe UI", 8))

        canvas.bind("<Configure>", lambda e: draw_bar())
        frame.after(50, draw_bar)

        rem_txt = (f"{rem} days remaining before limit"
                   if rem >= 0 else f"{abs(rem)} days OVER the limit")
        tk.Label(frame, text=rem_txt, font=("Segoe UI", 9),
                 bg=T["bg_panel"], fg=color).pack(anchor="center", pady=(2, 0))

    def _add_counts(self, counts):
        frame = tk.Frame(self, bg=T["bg_panel"])
        frame.pack(fill="x", padx=14, pady=2)
        self._keep(frame)
        for code, label, color in CATEGORIES:
            row = tk.Frame(frame, bg=T["bg_panel"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text="■", fg=color, bg=T["bg_panel"],
                     font=("Segoe UI", 12)).pack(side="left")
            tk.Label(row, text=label, bg=T["bg_panel"], fg=T["fg"],
                     font=("Segoe UI", 9), anchor="w").pack(side="left", padx=4, fill="x", expand=True)
            tk.Label(row, text=f"{counts[code]} days", bg=T["bg_panel"], fg=T["fg"],
                     font=("Segoe UI", 9, "bold")).pack(side="right")

    def _add_detail_metrics(self, result):
        frame = tk.Frame(self, bg=T["bg_panel"])
        frame.pack(fill="x", padx=14, pady=2)
        self._keep(frame)

        mfr_imp  = result["missions_france_imputed"]
        mhfr_imp = result["missions_hors_france_imputed"]
        hfr_exch = result["hfr_exchange_used"]
        rem_exch = result["remaining_hors_france"]

        def metric(label, value, fg=T["fg_dim"]):
            row = tk.Frame(frame, bg=T["bg_panel"])
            row.pack(fill="x", pady=1)
            tk.Label(row, text=label, bg=T["bg_panel"], fg=T["fg_dim"],
                     font=("Segoe UI", 8), anchor="w").pack(side="left")
            tk.Label(row, text=value, bg=T["bg_panel"], fg=fg,
                     font=("Segoe UI", 8, "bold")).pack(side="right")

        tk.Label(frame, text="Imputation details", bg=T["bg_panel"], fg=T["fg_dim"],
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 2))

        mhfr     = result["missions_hors_france"]
        nr       = result["non_retour_days"]
        metric("FR missions imputed (max 10, within 40%):",
               f"{mfr_imp} / 10 days", fg=T["fg"])
        metric("Outside-FR + non-return imputed (40% quota):",
               f"{mhfr_imp} days")
        metric("Outside-FR + non-return -> 2005 exchange:",
               f"{hfr_exch} / 45 days  ({mhfr} MXX + {nr} NRR)",
               fg=T["danger"] if hfr_exch > MAX_HORS_FR_EXCHANGE else T["fg"])
        metric("2005 exchange remaining:", f"{rem_exch} days")
        metric("Recorded working days:",
               f'{result["actual_days"]} days  →  quota {result["max_telework_days"]} days (40%)')


# ── Helpers ───────────────────────────────────────────────────────────────────

def _btn_kw() -> dict:
    return dict(
        bg=T["bg_panel"], fg=T["fg"],
        relief="flat", bd=0,
        activebackground=T["accent"], activeforeground=T["bg"],
        font=("Segoe UI", 10), padx=8, pady=3,
        cursor="hand2",
    )


def _apply_ttk_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        "TCombobox",
        fieldbackground=T["bg_cell"],
        background=T["bg_panel"],
        foreground=T["fg"],
        arrowcolor=T["fg"],
        selectbackground=T["accent"],
        selectforeground=T["bg"],
        bordercolor=T["separator"],
        lightcolor=T["separator"],
        darkcolor=T["separator"],
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", T["bg_cell"])],
        foreground=[("readonly", T["fg"])],
    )
