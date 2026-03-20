# -*- coding: utf-8 -*-
"""
PDF export — generates a compact yearly report via reportlab.
"""

import calendar
import datetime
import tkinter
from tkinter import messagebox

from constants import (
    CATEGORIES, MONTHS_EN, DAYS_EN,
    CAT_BUREAU, CAT_MAISON, CAT_EN_FR, CAT_HORS_FR, CAT_CONGE,
    CAT_COLOR,
)
from data import DataStore
from engine import compute_status


def export_pdf(store: DataStore, year: int, username: str, parent_window):
    """Export yearly data to a clean, compact PDF."""
    try:
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.colors import HexColor, white
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

    def hcol(h): return HexColor(int(h.lstrip("#"), 16))

    counts = store.year_counts(year)
    result = compute_status(counts)

    # ── Layout constants ──────────────────────────────────────────────────────
    W, H   = A4          # 595 x 842 pt
    ML, MR = 28, 28
    MT, MB = 28, 28
    USABLE_W = W - ML - MR    # 539 pt
    USABLE_H = H - MT - MB    # 786 pt

    HDR_H  = 64
    GAP    = 8
    SUM_H  = 152

    NCOLS, NROWS = 3, 4
    COL_GAP, ROW_GAP = 10, 12
    MONTH_W = (USABLE_W - (NCOLS - 1) * COL_GAP) / NCOLS
    MONTH_H = (USABLE_H - HDR_H - GAP - SUM_H - GAP - (NROWS - 1) * ROW_GAP) / NROWS

    MNTH_HDR_H = 16
    DAY_HDR_H  = 11
    GRID_H     = MONTH_H - MNTH_HDR_H - DAY_HDR_H - 4
    CELL_H     = GRID_H / 6
    CELL_W     = MONTH_W / 7

    BG_PAGE    = hcol("#F7F8FC")
    BG_MNTH    = hcol("#FFFFFF")
    BG_WEEKEND = hcol("#F0F0F4")
    BG_EMPTY   = hcol("#FAFAFA")
    FG_MAIN    = hcol("#1A1B2E")
    FG_DIM     = hcol("#888899")
    FG_WKEND   = hcol("#AAAABC")
    COL_BORDER = hcol("#DDDDEE")

    c = rl_canvas.Canvas(path, pagesize=A4)

    # ── Background ────────────────────────────────────────────────────────────
    c.setFillColor(BG_PAGE)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── Header ────────────────────────────────────────────────────────────────
    hdr_y = H - MT - HDR_H
    c.setFillColor(hcol("#1A1B2E"))
    c.roundRect(ML, hdr_y, USABLE_W, HDR_H, 4, fill=1, stroke=0)

    # Row 1 — title (top)
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(hcol("#7EB8F0"))
    c.drawString(ML + 14, hdr_y + HDR_H - 20, "Home Office Tracking")

    # Row 2 — subtitle (middle)
    c.setFont("Helvetica", 8)
    c.setFillColor(hcol("#6C6F9C"))
    c.drawString(ML + 14, hdr_y + HDR_H - 36,
                 "Franco-Swiss Agreement — April 11, 1983  |  Remote Work Tracking")

    # Row 3 — username badge (bottom), clearly below subtitle
    badge_w = min(200, 6.5 * len(username) + 28)
    c.setFillColor(hcol("#3A3B6A"))
    c.roundRect(ML + 14, hdr_y + 8, badge_w, 15, 3, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(hcol("#D0D3F0"))
    c.drawString(ML + 21, hdr_y + 12, f"  {username}")

    # Year (right)
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(white)
    c.drawRightString(ML + USABLE_W - 14, hdr_y + HDR_H - 26, str(year))

    c.setFont("Helvetica", 7)
    c.setFillColor(hcol("#6C6F9C"))
    generated = datetime.date.today().strftime("%B %d, %Y")
    c.drawRightString(ML + USABLE_W - 14, hdr_y + 8, f"Generated {generated}")

    # ── Month calendars ───────────────────────────────────────────────────────
    cal_top = hdr_y - GAP

    for month_idx in range(12):
        col = month_idx % NCOLS
        row = month_idx // NCOLS

        mx = ML + col * (MONTH_W + COL_GAP)
        my = cal_top - row * (MONTH_H + ROW_GAP) - MONTH_H

        # Month card background
        c.setFillColor(BG_MNTH)
        c.setStrokeColor(COL_BORDER)
        c.setLineWidth(0.5)
        c.roundRect(mx, my, MONTH_W, MONTH_H, 3, fill=1, stroke=1)

        # Month name header
        month_num = month_idx + 1
        c.setFillColor(hcol("#252640"))
        c.roundRect(mx, my + MONTH_H - MNTH_HDR_H, MONTH_W, MNTH_HDR_H, 3, fill=1, stroke=0)
        c.rect(mx, my + MONTH_H - MNTH_HDR_H, MONTH_W, MNTH_HDR_H / 2, fill=1, stroke=0)

        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(hcol("#7EB8F0"))
        c.drawCentredString(mx + MONTH_W / 2, my + MONTH_H - MNTH_HDR_H + 4,
                            MONTHS_EN[month_idx].upper())

        # Day-of-week headers
        day_hdr_y = my + MONTH_H - MNTH_HDR_H - DAY_HDR_H
        for di, dname in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
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
                c.drawCentredString(cx + CELL_W / 2, cy + CELL_H - 7.5, str(day_num))

                if cat:
                    abbrevs = {CAT_BUREAU: "OFF", CAT_MAISON: "HOM",
                               CAT_EN_FR: "MFR", CAT_HORS_FR: "MXX", CAT_CONGE: "VAC"}
                    c.setFont("Helvetica", 4.5)
                    c.setFillColor(white)
                    c.drawCentredString(cx + CELL_W / 2, cy + 1.5, abbrevs[cat])

    # ── Summary section ───────────────────────────────────────────────────────
    # Three horizontal bands (bottom → top):
    #   Band A (76pt): category counters
    #   Band B (36pt): key metrics
    #   Band C (40pt): title + status banner
    sum_y   = MB
    sum_top = sum_y + SUM_H          # sum_y + 152
    DIV_BC  = sum_top - 40           # top of Band B / bottom of Band C
    DIV_AB  = sum_y + 76             # top of Band A / bottom of Band B

    c.setFillColor(hcol("#1A1B2E"))
    c.roundRect(ML, sum_y, USABLE_W, SUM_H, 4, fill=1, stroke=0)

    # ── Band C: title + status banner ────────────────────────────────────────
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(hcol("#7EB8F0"))
    c.drawString(ML + 12, sum_top - 16, f"YEARLY SUMMARY — {year}  |  {username}")

    is_ok     = result["status"] == "ok"
    status_bg = hcol("#1B4332") if is_ok else hcol("#4A0A14")
    status_fg = hcol("#5CBF8A") if is_ok else hcol("#E85C6A")
    reason    = result["status_reason"].replace("\n", "  ")
    if len(reason) > 68:
        reason = reason[:65] + "…"

    c.setFillColor(status_bg)
    c.roundRect(ML + USABLE_W - 255, sum_top - 33, 243, 22, 3, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(status_fg)
    c.drawCentredString(ML + USABLE_W - 133, sum_top - 24, reason)

    # Divider B/C
    c.setStrokeColor(hcol("#3A3B5C"))
    c.setLineWidth(0.5)
    c.line(ML + 12, DIV_BC, ML + USABLE_W - 12, DIV_BC)

    # ── Band B: metrics row ───────────────────────────────────────────────────
    metrics = [
        ("Working days",       result["actual_days"]),
        ("Remote quota (40%)", result["max_telework_days"]),
        ("Effective remote",   result["effective_telework"]),
        ("Remote rate",        f"{result['telework_pct']:.1f}%"),
        ("Days remaining",     result["remaining_telework_days"]),
        ("2005 exchange",      f"{result['hfr_exchange_used']} / 45"),
    ]

    band_b_mid = (DIV_AB + DIV_BC) / 2      # vertical centre of Band B
    mw = USABLE_W / len(metrics)
    for i, (mlabel, mval) in enumerate(metrics):
        mx = ML + i * mw + mw / 2
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(white)
        c.drawCentredString(mx, band_b_mid + 5, str(mval))
        c.setFont("Helvetica", 6)
        c.setFillColor(hcol("#6C6F9C"))
        c.drawCentredString(mx, band_b_mid - 8, mlabel)

    # Divider A/B
    c.setStrokeColor(hcol("#3A3B5C"))
    c.setLineWidth(0.5)
    c.line(ML + 12, DIV_AB, ML + USABLE_W - 12, DIV_AB)

    # ── Band A: category counters ─────────────────────────────────────────────
    col_w = USABLE_W / len(CATEGORIES)
    for i, (code, label, color) in enumerate(CATEGORIES):
        cx      = ML + i * col_w + col_w / 2
        cy_base = sum_y + 8         # anchor near bottom of band

        sq = 10
        c.setFillColor(hcol(color))
        c.roundRect(cx - sq / 2, cy_base + 50, sq, sq, 2, fill=1, stroke=0)

        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(white)
        c.drawCentredString(cx, cy_base + 30, str(counts[code]))

        c.setFont("Helvetica", 7)
        c.setFillColor(hcol("#6C6F9C"))
        c.drawCentredString(cx, cy_base + 19, "days")

        short_label = label.replace(" (Switzerland)", "").replace(" (remote work)", "")
        c.setFont("Helvetica", 6.5)
        c.setFillColor(hcol("#D0D3F0"))
        c.drawCentredString(cx, cy_base + 8, short_label)

    c.save()
    messagebox.showinfo("PDF exported", f"File saved:\n{path}", parent=parent_window)
