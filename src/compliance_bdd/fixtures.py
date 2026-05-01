"""Domain → SQL-shape translators.

The fixture is the only place the UC function's argument shape is described.
Steps stay thin: parse the Given, call the fixture, pass the result to
call_rule. If the SQL function signature changes, only this file moves.
"""

from __future__ import annotations


def promo_history_to_lag_flags(promo_weeks: list[int]) -> tuple[bool, list[bool]]:
    """Translate "weeks the product was on promotion" into the UC function's input shape.

    The function expects:
      is_promoted          — TRUE if the current (latest) week is a promo week
      prev_promo_week_1..4 — TRUE if 1..4 weeks before the current week was a promo

    Example: weeks=[1, 6] means promoted in week 1, then again in week 6.
    Current week is 6. Week 1 is 5 weeks back — outside the 4-week window.
    All four lag flags are FALSE. Not back-to-back → compliant.
    """
    current_week = max(promo_weeks)
    promo_set = set(promo_weeks)
    lag_flags = [(current_week - lag) in promo_set for lag in (1, 2, 3, 4)]
    return current_week in promo_set, lag_flags
