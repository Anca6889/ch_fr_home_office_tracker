# Home Office Tracking

A desktop application for Franco-Swiss frontaliers to track remote work days and verify compliance with the **Franco-Swiss Agreement of April 11, 1983**.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![tkinter](https://img.shields.io/badge/UI-tkinter-lightgrey) ![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- Monthly calendar — click any weekday to assign a category
- Real-time compliance check against the 40% remote work quota
- 2005 bilateral exchange tracking (45-day annual cap on outside-France missions)
- Multi-user support with per-user data files
- PDF export — full-year calendar + summary in a single A4 page

## Legal basis

| Rule | Source |
|---|---|
| 40% telework quota | Franco-Swiss Agreement, April 11, 1983 + interpretive agreements 2022/2023 |
| 10-day cap on imputable missions | Same agreement |
| 45-day outside-France cap | Art. 1d + bilateral exchange of letters, February 21–24, 2005 |

### Work day categories

| Category | Counts toward 40% quota |
|---|---|
| Office (Switzerland) | No |
| Home (remote work) | Yes — fully |
| Mission in France | Yes — imputed first (max 10 days combined with outside-FR) |
| Mission outside France | Yes — imputed within remaining capacity; total capped at 45 days/year |
| Vacation / Sick leave | Not counted as a working day |

## Requirements

- Python 3.9 or later
- `reportlab` (only required for PDF export)

```
pip install reportlab
```

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/home-office-tracking.git
cd home-office-tracking
pip install reportlab   # optional, for PDF export
py home_office_tracking.py
```

## Project structure

```
home-office-tracking/
├── home_office_tracking.py   # Entry point — HomeOfficeApp shell
├── constants.py              # Category codes, thresholds, UI theme
├── data.py                   # UserManager, DataStore (JSON persistence)
├── engine.py                 # Compliance calculation engine
├── widgets.py                # CalendarWidget, SidePanel, ttk helpers
└── pdf_export.py             # PDF generation via reportlab
```

Data files (`home_office_*.json`) are created automatically in the same folder on first run and are excluded from version control.

## Usage

```
py home_office_tracking.py
```

- **Left click** a weekday → assign a category
- **Right click** → clear the day
- Use the **User** dropdown to switch between users (+ to add, ✕ to delete)
- Click **⬇ Export PDF** to generate the yearly report

## License

MIT
