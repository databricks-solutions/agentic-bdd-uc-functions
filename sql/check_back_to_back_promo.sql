-- The compliance rule: a Unity Catalog scalar function.
--
-- This is the single source of truth for the back-to-back promotion check.
-- Both callers use it without duplication:
--   1. BDD test suite  — via Statement Execution API (tests/bdd/)
--   2. Production pipeline — via SQL in the compliance_results materialized view
--
-- ${catalog} and ${schema} are substituted by scripts/deploy_function.py.

CREATE OR REPLACE FUNCTION ${catalog}.${schema}.check_back_to_back_promo(
  is_promoted        BOOLEAN,
  prev_promo_week_1  BOOLEAN,
  prev_promo_week_2  BOOLEAN,
  prev_promo_week_3  BOOLEAN,
  prev_promo_week_4  BOOLEAN
)
RETURNS BOOLEAN
COMMENT 'Returns TRUE when the product is promoted this week AND was promoted in any of the previous four weeks (violates the 4-week ACCC cooling period).'
RETURN
  is_promoted AND (
    COALESCE(prev_promo_week_1, FALSE) OR
    COALESCE(prev_promo_week_2, FALSE) OR
    COALESCE(prev_promo_week_3, FALSE) OR
    COALESCE(prev_promo_week_4, FALSE)
  );
