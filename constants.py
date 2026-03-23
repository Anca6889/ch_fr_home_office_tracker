# -*- coding: utf-8 -*-
"""
Shared constants — category codes, agreement thresholds, UI theme.
"""

# ── Category codes ────────────────────────────────────────────────────────────

CAT_BUREAU    = "bureau"
CAT_MAISON    = "maison"
CAT_EN_FR     = "en_france"
CAT_HORS_FR   = "hors_france"
CAT_NON_RETOUR = "non_retour"
CAT_CONGE     = "conge"

CATEGORIES = [
    (CAT_BUREAU,     "Office (Switzerland)",   "#4A90D9"),
    (CAT_MAISON,     "Home (remote work)",     "#27AE60"),
    (CAT_EN_FR,      "Mission in France",      "#E74C3C"),
    (CAT_HORS_FR,    "Mission outside France", "#9B59B6"),
    (CAT_NON_RETOUR, "Non-return day",         "#E67E22"),
    (CAT_CONGE,      "Vacation / Sick leave",  "#7F8C8D"),
]

CAT_LABEL = {k: lbl for k, lbl, _   in CATEGORIES}
CAT_COLOR = {k: col for k, _,   col in CATEGORIES}

# ── Franco-Swiss agreement thresholds ────────────────────────────────────────

TELEWORK_RATE        = 0.40
MAX_MISSION_IMPUTED  = 10
MAX_HORS_FR_EXCHANGE = 45

# ── Calendar labels ───────────────────────────────────────────────────────────

MONTHS_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
DAYS_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# ── UI themes ─────────────────────────────────────────────────────────────────

DARK_THEME = {
    "bg":               "#1A1B2E",
    "bg_panel":         "#252640",
    "bg_cell":          "#2E2F50",
    "bg_cell_wk":       "#1E1F35",
    "bg_today":         "#3A3B6A",
    "fg":               "#D0D3F0",
    "fg_dim":           "#6C6F9C",
    "ok":               "#5CBF8A",
    "danger":           "#E85C6A",
    "accent":           "#7EB8F0",
    "separator":        "#3A3B5C",
    "status_ok_bg":     "#1B4332",
    "status_danger_bg": "#4A0A14",
    "btn_export_bg":    "#2C4A7C",
    "btn_export_fg":    "#7EB8F0",
}

LIGHT_THEME = {
    "bg":               "#F5F6FA",
    "bg_panel":         "#FFFFFF",
    "bg_cell":          "#EEEFF8",
    "bg_cell_wk":       "#E4E5EF",
    "bg_today":         "#D6E4F7",
    "fg":               "#1A1B2E",
    "fg_dim":           "#6C6F9C",
    "ok":               "#27AE60",
    "danger":           "#D63649",
    "accent":           "#2A6FBA",
    "separator":        "#CCCEE0",
    "status_ok_bg":     "#D5F5E3",
    "status_danger_bg": "#FAD7DA",
    "btn_export_bg":    "#2A6FBA",
    "btn_export_fg":    "#FFFFFF",
}

# Mutable dict — updated in-place when the user toggles the theme.
T = dict(DARK_THEME)
