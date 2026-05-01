"""Step definitions for back_to_back_promo.feature.

Steps are thin by design: parse the Given, translate via fixture, call the
UC function, assert the result. The rule itself lives in Unity Catalog.
"""

from __future__ import annotations

from behave import given, then, when

from compliance_bdd.fixtures import promo_history_to_lag_flags
from compliance_bdd.spark_rules import call_rule


@given("a product was promoted in weeks {weeks}")
def step_given_promo_weeks(context, weeks: str) -> None:
    context.promo_weeks = [int(w.strip()) for w in weeks.split(",")]


@when("I check for back-to-back promotions")
def step_when_check(context) -> None:
    is_promoted, lag_flags = promo_history_to_lag_flags(context.promo_weeks)
    args = ", ".join([str(is_promoted).upper()] + [str(f).upper() for f in lag_flags])
    context.result = "FAILED" if call_rule(f"check_back_to_back_promo({args})") else "PASSED"


@then('the result should be "{expected}"')
def step_then_result(context, expected: str) -> None:
    assert context.result == expected, (
        f"Expected {expected!r} but got {context.result!r} "
        f"for promo_weeks={context.promo_weeks}"
    )
