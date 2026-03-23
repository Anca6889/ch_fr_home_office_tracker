# -*- coding: utf-8 -*-
"""
Compliance engine — Franco-Swiss Agreement of April 11, 1983.

Implements the 40% telework quota rule and the 2005 bilateral exchange
(45-day annual cap on outside-France missions).
"""

from constants import (
    CAT_BUREAU, CAT_MAISON, CAT_EN_FR, CAT_HORS_FR, CAT_NON_RETOUR,
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
    outside France without losing their frontalier status (art. 1d + echange
    de lettres 21-24 fev. 2005). This cap applies to the COMBINED total of
    outside-France mission days AND non-return days.
    If total (hors_france + non_retour) > 45 -> agreement inapplicable.
    """
    domicile     = counts[CAT_MAISON]
    missions_fr  = counts[CAT_EN_FR]
    missions_hfr = counts[CAT_HORS_FR]
    non_retour   = counts.get(CAT_NON_RETOUR, 0)
    bureau       = counts[CAT_BUREAU]

    total_outside_fr  = missions_hfr + non_retour
    actual_days       = bureau + domicile + missions_fr + missions_hfr + non_retour
    max_telework_days = int(actual_days * TELEWORK_RATE)

    # Capacity remaining in the 40% quota after home days
    quota_remaining = max(0, max_telework_days - domicile)
    # Combined 10-day cap AND quota cap (whichever is more restrictive)
    max_imputable   = min(MAX_MISSION_IMPUTED, quota_remaining)

    # ── Rule 1: all France missions must be imputable ─────────────────────────
    if missions_fr > max_imputable:
        tw_pct = (domicile / actual_days * 100) if actual_days else 0.0
        return _make_result(
            counts, domicile, missions_fr, missions_hfr, non_retour,
            actual_days, max_telework_days, quota_remaining,
            mfr_imp=0, mhfr_imp=0,
            eff_tw=domicile, tw_pct=tw_pct,
            rem_tw=quota_remaining,
            status="danger",
            reason=(
                f"\u26a0 France missions cannot be fully imputed\n"
                f"{missions_fr} days > {max_imputable} max imputable\n"
                f"({'quota insufficient - ' if missions_fr <= MAX_MISSION_IMPUTED else ''}agreement inapplicable)"
            ),
        )

    mfr_imp = missions_fr   # all France missions imputed (priority 1)

    # Remaining combined capacity for outside-France + non-return missions
    cap_hfr  = max_imputable - mfr_imp
    mhfr_imp = min(total_outside_fr, cap_hfr)   # combined imputed within 40% quota

    eff_tw = domicile + mfr_imp + mhfr_imp
    tw_pct = (eff_tw / actual_days * 100) if actual_days else 0.0
    rem_tw = max_telework_days - eff_tw

    # ── Rule 2: TOTAL outside-France + non-return days <= 45 (2005 exchange) ──
    if total_outside_fr > MAX_HORS_FR_EXCHANGE:
        return _make_result(
            counts, domicile, missions_fr, missions_hfr, non_retour,
            actual_days, max_telework_days, quota_remaining,
            mfr_imp, mhfr_imp, eff_tw, tw_pct, rem_tw,
            status="danger",
            reason=(
                f"\u26a0 2005 exchange limit exceeded\n"
                f"Outside-France + non-return: {total_outside_fr} days > 45\n"
                f"\u2192 Agreement inapplicable"
            ),
        )

    # ── Rule 3: effective telework <= 40% (safety check) ─────────────────────
    if tw_pct > 40.0:
        return _make_result(
            counts, domicile, missions_fr, missions_hfr, non_retour,
            actual_days, max_telework_days, quota_remaining,
            mfr_imp, mhfr_imp, eff_tw, tw_pct, rem_tw,
            status="danger",
            reason=(
                f"\u26a0 Remote work quota exceeded ({tw_pct:.1f}% > 40%)\n"
                f"\u2192 Agreement inapplicable"
            ),
        )

    # ── All good ──────────────────────────────────────────────────────────────
    if rem_tw == 0:
        reason = f"\u2713 Remote work quota reached ({tw_pct:.1f}%) - stay in the office"
    elif rem_tw <= 3:
        reason = f"\u2713 Status OK - only {rem_tw} remote day(s) remaining"
    else:
        reason = f"\u2713 Frontalier status compliant  -  {rem_tw} days remaining"

    return _make_result(
        counts, domicile, missions_fr, missions_hfr, non_retour,
        actual_days, max_telework_days, quota_remaining,
        mfr_imp, mhfr_imp, eff_tw, tw_pct, rem_tw,
        status="ok", reason=reason,
    )


def _make_result(counts, domicile, mfr, mhfr, non_retour,
                 actual_days, max_telework_days, quota_rem,
                 mfr_imp, mhfr_imp, eff_tw, tw_pct, rem_tw,
                 status, reason):
    total_outside_fr = mhfr + non_retour
    return {
        "counts":                       counts,
        "actual_days":                  actual_days,
        "max_telework_days":            max_telework_days,
        "domicile_days":                domicile,
        "missions_france":              mfr,
        "missions_hors_france":         mhfr,
        "non_retour_days":              non_retour,
        "quota_remaining":              quota_rem,
        "missions_france_imputed":      mfr_imp,
        "missions_hors_france_imputed": mhfr_imp,
        "effective_telework":           eff_tw,
        "telework_pct":                 tw_pct,
        "remaining_telework_days":      rem_tw,
        "hfr_exchange_used":            total_outside_fr,
        "remaining_hors_france":        MAX_HORS_FR_EXCHANGE - total_outside_fr,
        "status":                       status,
        "status_reason":                reason,
    }
