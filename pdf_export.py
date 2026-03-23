# -*- coding: utf-8 -*-
"""
PDF export -- generates a compact 3-page yearly report (EN / FR / DE) via reportlab.
"""

import calendar
import datetime
import tkinter
from tkinter import messagebox

from constants import (
    CATEGORIES, CAT_BUREAU, CAT_MAISON, CAT_EN_FR,
    CAT_HORS_FR, CAT_NON_RETOUR, CAT_CONGE, CAT_COLOR,
)
from data import DataStore
from engine import compute_status


# ── Locale definitions ────────────────────────────────────────────────────────
# catShortLabels order matches CATEGORIES list in constants.py:
#   bureau, maison, en_france, hors_france, non_retour, conge

_LOCALES = {
    "en": {
        "title":           "Home Office Tracking",
        "subtitle":        "Franco-Swiss frontier worker - telework & temporary mission day tracker",
        "gen_prefix":      "Generated",
        "yearly_summary":  "YEARLY SUMMARY",
        "days":            "days",
        "metrics":         ["Working days", "Remote quota (40%)", "Effective remote",
                            "Remote rate", "Days remaining", "2005 exch. (MXX+NRR)"],
        "cat_short":       ["Office", "Home", "Mission FR", "Outside FR", "Non-return", "Vacation"],
        "months":          ["January", "February", "March", "April", "May", "June",
                            "July", "August", "September", "October", "November", "December"],
        "day_letters":     ["M", "T", "W", "T", "F", "S", "S"],
    },
    "fr": {
        "title":           "Suivi Teletravail",
        "subtitle":        "Frontalier franco-suisse - suivi des jours de teletravail et missions temporaires",
        "gen_prefix":      "Genere le",
        "yearly_summary":  "RESUME ANNUEL",
        "days":            "jours",
        "metrics":         ["Jours travailles", "Quota TT (40%)", "TT effectif",
                            "Taux TT", "Jours restants", "Echange 2005 (MXX+NRR)"],
        "cat_short":       ["Bureau", "Domicile", "Mission FR", "Hors FR", "Non-retour", "Conge"],
        "months":          ["Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin",
                            "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Decembre"],
        "day_letters":     ["L", "M", "M", "J", "V", "S", "D"],
    },
    "de": {
        "title":           "Homeoffice-Tracking",
        "subtitle":        "Grenzganger Frankreich-Schweiz - Erfassung von Homeoffice- und Missionstagen",
        "gen_prefix":      "Erstellt am",
        "yearly_summary":  "JAHRESUBERSICHT",
        "days":            "Tage",
        "metrics":         ["Arbeitstage", "HO-Quote (40%)", "Eff. Homeoffice",
                            "HO-Rate", "Verbl. Tage", "Austausch 2005 (MXX+NRR)"],
        "cat_short":       ["Buro", "Zuhause", "Mission FR", "Auss. FR", "Nichtruckkehr", "Urlaub"],
        "months":          ["Januar", "Februar", "Marz", "April", "Mai", "Juni",
                            "Juli", "August", "September", "Oktober", "November", "Dezember"],
        "day_letters":     ["M", "D", "M", "D", "F", "S", "S"],
    },
}

_ABBREVS = {
    CAT_BUREAU:     "OFF",
    CAT_MAISON:     "HOM",
    CAT_EN_FR:      "MFR",
    CAT_HORS_FR:    "MXX",
    CAT_NON_RETOUR: "NRR",
    CAT_CONGE:      "VAC",
}


def _formatted_date(lang, today, months):
    if lang == "fr":
        return f"{today.day} {months[today.month - 1].lower()} {today.year}"
    if lang == "de":
        return f"{today.day}. {months[today.month - 1]} {today.year}"
    return today.strftime("%B %d, %Y")


# ── Flag drawing ──────────────────────────────────────────────────────────────

def _draw_flag(c, lang, x, y, w, h, hcol, white, black):
    """Draw a country flag at position (x, y) with size (w x h) points."""
    if lang == "fr":
        # Vertical tricolour: blue | white | red
        bw = w / 3
        c.setFillColor(hcol("#002395")); c.rect(x,        y, bw, h, fill=1, stroke=0)
        c.setFillColor(white);           c.rect(x + bw,   y, bw, h, fill=1, stroke=0)
        c.setFillColor(hcol("#ED2939")); c.rect(x + 2*bw, y, bw, h, fill=1, stroke=0)

    elif lang == "de":
        # Horizontal tricolour: black | red | gold (top to bottom)
        bh = h / 3
        c.setFillColor(black);           c.rect(x, y + 2*bh, w, bh, fill=1, stroke=0)
        c.setFillColor(hcol("#DD0000")); c.rect(x, y + bh,   w, bh, fill=1, stroke=0)
        c.setFillColor(hcol("#FFCE00")); c.rect(x, y,        w, bh, fill=1, stroke=0)

    else:
        # Union Jack -- layers: blue bg, white X, red X, white +, red +
        # Clip all drawing to the flag rectangle
        c.saveState()
        p = c.beginPath()
        p.rect(x, y, w, h)
        c.clipPath(p, stroke=0, fill=0)

        c.setFillColor(hcol("#012169"))
        c.rect(x, y, w, h, fill=1, stroke=0)

        # White X (St Andrew's cross)
        c.setStrokeColor(white)
        c.setLineWidth(h * 0.22)
        c.line(x,   y,   x+w, y+h)   # bottom-left to top-right
        c.line(x,   y+h, x+w, y)     # top-left to bottom-right

        # Red X (St Patrick's cross, thinner)
        c.setStrokeColor(hcol("#C8102E"))
        c.setLineWidth(h * 0.11)
        c.line(x,   y,   x+w, y+h)
        c.line(x,   y+h, x+w, y)

        # White + cross (St George's, wide)
        c.setStrokeColor(white)
        c.setLineWidth(h * 0.38)
        c.line(x, y+h/2, x+w, y+h/2)
        c.line(x+w/2, y, x+w/2, y+h)

        # Red + cross (narrower)
        c.setStrokeColor(hcol("#C8102E"))
        c.setLineWidth(h * 0.22)
        c.line(x, y+h/2, x+w, y+h/2)
        c.line(x+w/2, y, x+w/2, y+h)

        c.restoreState()

    # Frame border (drawn after restoreState so it is not clipped)
    c.setStrokeColor(hcol("#BBBBCC"))
    c.setLineWidth(0.4)
    c.rect(x, y, w, h, fill=0, stroke=1)


# ── Entry point ───────────────────────────────────────────────────────────────

def export_pdf(store: DataStore, year: int, username: str, parent_window):
    """Export yearly data to a 3-page PDF (English / French / German)."""
    try:
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.colors import HexColor, white, black
    except ImportError:
        messagebox.showerror(
            "Missing dependency",
            "reportlab is required for PDF export.\n\nInstall it with:\n  pip install reportlab",
            parent=parent_window,
        )
        return

    from tkinter import filedialog
    safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in username)
    path = filedialog.asksaveasfilename(
        parent=parent_window,
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=f"home_office_{safe_name}_{year}.pdf",
        title="Export PDF",
    )
    if not path:
        return

    def hcol(h):
        return HexColor(int(h.lstrip("#"), 16))

    counts = store.year_counts(year)
    result = compute_status(counts)

    # ── Layout constants (same for all pages) ─────────────────────────────────
    W, H   = A4          # 595 x 842 pt
    ML, MR = 28, 28
    MT, MB = 28, 28
    USABLE_W = W - ML - MR
    USABLE_H = H - MT - MB

    HDR_H  = 64
    GAP    = 8
    SUM_H  = 162         # taller than before to fit larger status badge

    NCOLS, NROWS = 3, 4
    COL_GAP, ROW_GAP = 10, 12
    MONTH_W = (USABLE_W - (NCOLS - 1) * COL_GAP) / NCOLS
    MONTH_H = (USABLE_H - HDR_H - GAP - SUM_H - GAP - (NROWS - 1) * ROW_GAP) / NROWS

    MNTH_HDR_H = 16
    DAY_HDR_H  = 11
    GRID_H     = MONTH_H - MNTH_HDR_H - DAY_HDR_H - 4
    CELL_H     = GRID_H / 6
    CELL_W     = MONTH_W / 7

    FLAG_W, FLAG_H = 30, 20

    # ── PDF colour palette ────────────────────────────────────────────────────
    HDR_BG     = hcol("#EEF0FB")
    MNTH_HDR   = hcol("#DDE0F5")
    ACCENT     = hcol("#2A5FA8")
    FG_MAIN    = hcol("#1A1B2E")
    FG_DIM     = hcol("#6C6F9C")
    BG_MNTH    = hcol("#FFFFFF")
    BG_WEEKEND = hcol("#F0F0F4")
    BG_EMPTY   = hcol("#FAFAFA")
    BG_PAGE    = hcol("#F7F8FC")
    FG_WKEND   = hcol("#AAAABC")
    COL_BORDER = hcol("#DDDDEE")

    c = rl_canvas.Canvas(path, pagesize=A4)
    today = datetime.date.today()

    for lang in ("en", "fr", "de"):
        loc = _LOCALES[lang]

        # ── Page background ───────────────────────────────────────────────────
        c.setFillColor(BG_PAGE)
        c.rect(0, 0, W, H, fill=1, stroke=0)

        # ── Header ────────────────────────────────────────────────────────────
        hdr_y = H - MT - HDR_H
        c.setFillColor(HDR_BG)
        c.setStrokeColor(COL_BORDER)
        c.setLineWidth(0.5)
        c.roundRect(ML, hdr_y, USABLE_W, HDR_H, 4, fill=1, stroke=1)

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(ACCENT)
        c.drawString(ML + 14, hdr_y + HDR_H - 20, loc["title"])

        # Subtitle
        c.setFont("Helvetica", 7.5)
        c.setFillColor(FG_DIM)
        c.drawString(ML + 14, hdr_y + HDR_H - 34, loc["subtitle"])

        # Username badge
        badge_w = min(200, 6.5 * len(username) + 28)
        c.setFillColor(MNTH_HDR)
        c.roundRect(ML + 14, hdr_y + 8, badge_w, 15, 3, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(FG_MAIN)
        c.drawString(ML + 21, hdr_y + 12, f"  {username}")

        # Flag + year (right side)
        year_w  = c.stringWidth(str(year), "Helvetica-Bold", 22)
        flag_x  = ML + USABLE_W - 14 - year_w - 10 - FLAG_W
        flag_y  = hdr_y + HDR_H - 8 - FLAG_H
        _draw_flag(c, lang, flag_x, flag_y, FLAG_W, FLAG_H, hcol, white, black)

        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(FG_MAIN)
        c.drawRightString(ML + USABLE_W - 14, hdr_y + HDR_H - 26, str(year))

        # Generated date
        c.setFont("Helvetica", 7)
        c.setFillColor(FG_DIM)
        gen_date = _formatted_date(lang, today, loc["months"])
        c.drawRightString(ML + USABLE_W - 14, hdr_y + 8,
                          f"{loc['gen_prefix']} {gen_date}")

        # ── Month calendars ───────────────────────────────────────────────────
        cal_top = hdr_y - GAP

        for month_idx in range(12):
            col = month_idx % NCOLS
            row = month_idx // NCOLS

            mx = ML + col * (MONTH_W + COL_GAP)
            my = cal_top - row * (MONTH_H + ROW_GAP) - MONTH_H

            c.setFillColor(BG_MNTH)
            c.setStrokeColor(COL_BORDER)
            c.setLineWidth(0.5)
            c.roundRect(mx, my, MONTH_W, MONTH_H, 3, fill=1, stroke=1)

            # Month name header
            month_num = month_idx + 1
            c.setFillColor(MNTH_HDR)
            c.roundRect(mx, my + MONTH_H - MNTH_HDR_H,
                        MONTH_W, MNTH_HDR_H, 3, fill=1, stroke=0)
            c.rect(mx, my + MONTH_H - MNTH_HDR_H,
                   MONTH_W, MNTH_HDR_H / 2, fill=1, stroke=0)

            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(ACCENT)
            c.drawCentredString(mx + MONTH_W / 2,
                                my + MONTH_H - MNTH_HDR_H + 4,
                                loc["months"][month_idx].upper())

            # Day-of-week headers
            day_hdr_y = my + MONTH_H - MNTH_HDR_H - DAY_HDR_H
            for di, dname in enumerate(loc["day_letters"]):
                dx = mx + di * CELL_W + CELL_W / 2
                c.setFont("Helvetica-Bold", 6)
                c.setFillColor(FG_WKEND if di >= 5 else FG_DIM)
                c.drawCentredString(dx, day_hdr_y + 2, dname)

            # Day cells
            month_data = store.month_days(year, month_num)
            cal_weeks  = calendar.monthcalendar(year, month_num)
            while len(cal_weeks) < 6:
                cal_weeks.append([0] * 7)

            for week_i, week in enumerate(cal_weeks):
                for dow, day_num in enumerate(week):
                    cx = mx + dow * CELL_W
                    cy = day_hdr_y - (week_i + 1) * CELL_H

                    if day_num == 0:
                        c.setFillColor(BG_EMPTY)
                        c.setStrokeColor(COL_BORDER)
                        c.setLineWidth(0.3)
                        c.rect(cx, cy, CELL_W, CELL_H, fill=1, stroke=1)
                        continue

                    cat      = month_data.get(str(day_num))
                    is_wkend = dow >= 5

                    if cat:
                        bg     = hcol(CAT_COLOR[cat])
                        num_fg = white
                    elif is_wkend:
                        bg     = BG_WEEKEND
                        num_fg = FG_WKEND
                    else:
                        bg     = BG_MNTH
                        num_fg = FG_MAIN

                    c.setFillColor(bg)
                    c.setStrokeColor(COL_BORDER)
                    c.setLineWidth(0.3)
                    c.rect(cx, cy, CELL_W, CELL_H, fill=1, stroke=1)

                    c.setFont("Helvetica-Bold" if cat else "Helvetica", 6.5)
                    c.setFillColor(num_fg)
                    c.drawCentredString(cx + CELL_W / 2, cy + CELL_H - 7.5,
                                        str(day_num))

                    if cat:
                        c.setFont("Helvetica", 4.5)
                        c.setFillColor(white)
                        c.drawCentredString(cx + CELL_W / 2, cy + 1.5,
                                            _ABBREVS.get(cat, ""))

        # ── Summary section ───────────────────────────────────────────────────
        sum_y   = MB
        sum_top = sum_y + SUM_H
        DIV_BC  = sum_top - 46          # taller band C for bigger status badge
        DIV_AB  = sum_y + 76

        c.setFillColor(HDR_BG)
        c.setStrokeColor(COL_BORDER)
        c.setLineWidth(0.5)
        c.roundRect(ML, sum_y, USABLE_W, SUM_H, 4, fill=1, stroke=1)

        # ── Band C: title + status badge ──────────────────────────────────────
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(ACCENT)
        c.drawString(ML + 12, sum_top - 16,
                     f"{loc['yearly_summary']} - {year}  |  {username}")

        is_ok     = result["status"] == "ok"
        status_bg = hcol("#D5F5E3") if is_ok else hcol("#FAD7DA")
        status_fg = hcol("#1B6B3A") if is_ok else hcol("#8B2030")

        # Language-neutral status line: percentage + used/allowed days
        status_line = (f"{result['telework_pct']:.1f}%"
                       f"  -  {result['effective_telework']}"
                       f" / {result['max_telework_days']} {loc['days']}")

        badge_text_w = c.stringWidth(status_line, "Helvetica-Bold", 11)
        badge_w_sum  = badge_text_w + 20
        badge_h_sum  = 22
        badge_x      = ML + USABLE_W - 14 - badge_w_sum
        badge_y      = sum_top - 14 - badge_h_sum

        c.setFillColor(status_bg)
        c.roundRect(badge_x, badge_y, badge_w_sum, badge_h_sum, 4, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(status_fg)
        c.drawCentredString(badge_x + badge_w_sum / 2,
                            badge_y + badge_h_sum / 2 - 4,
                            status_line)

        # Divider B/C
        c.setStrokeColor(COL_BORDER)
        c.setLineWidth(0.5)
        c.line(ML + 12, DIV_BC, ML + USABLE_W - 12, DIV_BC)

        # ── Band B: metrics row ───────────────────────────────────────────────
        metric_values = [
            result["actual_days"],
            result["max_telework_days"],
            result["effective_telework"],
            f"{result['telework_pct']:.1f}%",
            result["remaining_telework_days"],
            f"{result['hfr_exchange_used']} / 45",
        ]
        band_b_mid = (DIV_AB + DIV_BC) / 2
        mw = USABLE_W / len(loc["metrics"])
        for i, (mlabel, mval) in enumerate(zip(loc["metrics"], metric_values)):
            mx = ML + i * mw + mw / 2
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(FG_MAIN)
            c.drawCentredString(mx, band_b_mid + 5, str(mval))
            c.setFont("Helvetica", 6)
            c.setFillColor(FG_DIM)
            c.drawCentredString(mx, band_b_mid - 8, mlabel)

        # Divider A/B
        c.setStrokeColor(COL_BORDER)
        c.setLineWidth(0.5)
        c.line(ML + 12, DIV_AB, ML + USABLE_W - 12, DIV_AB)

        # ── Band A: category counters ─────────────────────────────────────────
        col_w = USABLE_W / len(CATEGORIES)
        for i, (code, _label, color) in enumerate(CATEGORIES):
            cx      = ML + i * col_w + col_w / 2
            cy_base = sum_y + 8
            short   = loc["cat_short"][i]

            sq = 10
            c.setFillColor(hcol(color))
            c.roundRect(cx - sq / 2, cy_base + 50, sq, sq, 2, fill=1, stroke=0)

            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(FG_MAIN)
            c.drawCentredString(cx, cy_base + 30, str(counts[code]))

            c.setFont("Helvetica", 7)
            c.setFillColor(FG_DIM)
            c.drawCentredString(cx, cy_base + 19, loc["days"])

            c.setFont("Helvetica", 6.5)
            c.setFillColor(FG_DIM)
            c.drawCentredString(cx, cy_base + 8, short)

        c.showPage()

    c.save()
    messagebox.showinfo("PDF exported", f"File saved:\n{path}", parent=parent_window)
