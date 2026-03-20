# -*- coding: utf-8 -*-
"""
Compliance engine — Franco-Swiss Agreement of April 11, 1983.

Implements the 40% telework quota rule and the 2005 bilateral exchange
(45-day annual cap on outside-France missions).
"""

from constants import (
    CAT_BUREAU, CAT_MAISON, CAT_EN_FR, CAT_HORS_FR,
    TELEWORK_RATE, MAX_MISSION_IMPUTED, MAX_HORS_FR_EXCHANGE,
)


def compute_status(counts: dict) -> dict:
    """
    Franco-Swiss Agreement of April 11, 1983 + interpretive agreements (2022, 2023).

    ── 40% rule ──────────────────────────────────────────────────────────────
    Home days count fully toward the 40% quota.

    Temporary missions (France + outside-France combined) can be assimilated to
    telework up to BOTH limits simultaneously:
      (a) max 10 days/year combined, AND
      (b) the remaining capacity in the 40% quota (after home days).

    Priority order for imputation: home days first, then France missions,
    then outside-France missions.

    If ALL France mission days cannot be imputed (quota or 10-day limit) → inapplicable.

    ── 2005 exchange (45-day rule) ────────────────────────────────────────────
    The 2005 bilateral exchange allows frontaliers to spend up to 45 days/year
    outside France without losing their frontalier status (art. 1d + échange
    de lettres 21-24 fév. 2005). This is an ANNUAL TOTAL cap on all
    outside-France (third-state) mission days, regardless of whether some of
    those days were imputed within the 40% quota.
    If total outside-France days > 45 → agreement inapplicable.
    """
    domicile     = counts[CAT_MAISON]
    missions_fr  = counts[CAT_EN_FR]
    missions_hfr = counts[CAT_HORS_FR]
    bureau       = counts[CAT_BUREAU]

    actual_days       = bureau + domicile + missions_fr + missions_hfr
    max_telework_days = int(actual_days * TELEWORK_RATE)

    # Capacity remaining in the 40% quota after home days
    quota_remaining = max(0, max_telework_days - domicile)
    # Combined 10-day cap AND quota cap (whichever is more restrictive)
    max_imputable   = min(MAX_MISSION_IMPUTED, quota_remaining)

    # ── Rule 1: all France missions must be imputable ─────────────────────────
    # (quota remaining after home days, combined with outside-FR, max 10 total)
    if missions_fr > max_imputable:
        tw_pct = (domicile / actual_days * 100) if actual_days else 0.0
        return _make_result(
            counts, domicile, missions_fr, missions_hfr,
            actual_days, max_telework_days, quota_remaining,
            mfr_imp=0, mhfr_imp=0,
            eff_tw=domicile, tw_pct=tw_pct,
            rem_tw=quota_remaining,
            status="danger",
            reason=(
                f"⚠ France missions cannot be fully imputed\n"
                f"{missions_fr} days > {max_imputable} max imputable\n"
                f"({'quota insufficient — ' if missions_fr <= MAX_MISSION_IMPUTED else ''}agreement inapplicable)"
            ),
        )

    mfr_imp = missions_fr   # all France missions imputed (priority 1)

    # Remaining combined capacity for outside-France missions
    cap_hfr  = max_imputable - mfr_imp
    mhfr_imp = min(missions_hfr, cap_hfr)   # outside-FR imputed within 40% quota

    eff_tw = domicile + mfr_imp + mhfr_imp
    tw_pct = (eff_tw / actual_days * 100) if actual_days else 0.0
    rem_tw = max_telework_days - eff_tw

    # ── Rule 2: TOTAL outside-France days ≤ 45 (2005 exchange) ──────────────
    # The 45-day ceiling is an annual absolute cap on all outside-France days
    # (art. 1d + échange de lettres 2005), not just the non-imputed portion.
    if missions_hfr > MAX_HORS_FR_EXCHANGE:
        return _make_result(
            counts, domicile, missions_fr, missions_hfr,
            actual_days, max_telework_days, quota_remaining,
            mfr_imp, mhfr_imp, eff_tw, tw_pct, rem_tw,
            status="danger",
            reason=(
                f"⚠ 2005 exchange limit exceeded\n"
                f"Total outside-France: {missions_hfr} days > 45\n"
                f"→ Agreement inapplicable"
            ),
        )

    # ── Rule 3: effective telework ≤ 40% (safety check) ──────────────────────
    if tw_pct > 40.0:
        return _make_result(
            counts, domicile, missions_fr, missions_hfr,
            actual_days, max_telework_days, quota_remaining,
            mfr_imp, mhfr_imp, eff_tw, tw_pct, rem_tw,
            status="danger",
            reason=(
                f"⚠ Remote work quota exceeded ({tw_pct:.1f}% > 40%)\n"
                f"→ Agreement inapplicable"
            ),
        )

    # ── All good ──────────────────────────────────────────────────────────────
    if rem_tw == 0:
        reason = f"✓ Remote work quota reached ({tw_pct:.1f}%) — stay in the office"
    elif rem_tw <= 3:
        reason = f"✓ Status OK — only {rem_tw} remote day(s) remaining"
    else:
        reason = f"✓ Frontalier status compliant  —  {rem_tw} days remaining"

    return _make_result(
        counts, domicile, missions_fr, missions_hfr,
        actual_days, max_telework_days, quota_remaining,
        mfr_imp, mhfr_imp, eff_tw, tw_pct, rem_tw,
        status="ok", reason=reason,
    )


def _make_result(counts, domicile, mfr, mhfr,
                 actual_days, max_telework_days, quota_rem,
                 mfr_imp, mhfr_imp, eff_tw, tw_pct, rem_tw,
                 status, reason):
    return {
        "counts":                       counts,
        "actual_days":                  actual_days,
        "max_telework_days":            max_telework_days,
        "domicile_days":                domicile,
        "missions_france":              mfr,
        "missions_hors_france":         mhfr,
        "quota_remaining":              quota_rem,
        "missions_france_imputed":      mfr_imp,
        "missions_hors_france_imputed": mhfr_imp,   # imputed within 40% quota
        "effective_telework":           eff_tw,      # home + mfr_imp + mhfr_imp
        "telework_pct":                 tw_pct,      # eff_tw / actual (≤ 40% when compliant)
        "remaining_telework_days":      rem_tw,      # max_telework - eff_tw
        "hfr_exchange_used":            mhfr,        # total outside-FR (annual cap = 45)
        "remaining_hors_france":        MAX_HORS_FR_EXCHANGE - mhfr,
        "status":                       status,
        "status_reason":                reason,
    }
