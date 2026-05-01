"""Lakeflow Spark Declarative Pipeline — compliance layer.

The production pipeline calls the same UC function the BDD tests validate.
The business rule lives once in Unity Catalog; both callers reference it
without duplication.

Pipeline configuration (set via databricks.yml resources/pipeline.yml):
  bdd.catalog — the UC catalog where check_back_to_back_promo is deployed
  bdd.schema  — the UC schema where check_back_to_back_promo is deployed

Note: this file is a workspace artifact, not a Python package. It lives in
pipelines/ (not src/) because the Lakeflow runtime discovers and executes it
directly — it cannot be installed as a wheel entry point.
"""

from __future__ import annotations

import dlt
from pyspark.sql import functions as F

# Read from pipeline configuration so this file is target-agnostic.
# Set bdd.catalog and bdd.schema in resources/pipeline.yml.
CATALOG = spark.conf.get("bdd.catalog", "main")
SCHEMA = spark.conf.get("bdd.schema", "compliance")


@dlt.table(
    name="bronze_promotions",
    comment="Raw weekly promotion records ingested from source",
)
def bronze_promotions():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", f"/Volumes/{CATALOG}/{SCHEMA}/checkpoints/schema")
        .load(f"/Volumes/{CATALOG}/{SCHEMA}/raw/promotions")
    )


@dlt.table(
    name="silver_timeline",
    comment="Cleaned weekly promotion timeline per product and location",
)
def silver_timeline():
    return dlt.read_stream("bronze_promotions").select(
        F.col("product_id").cast("string"),
        F.col("location_id").cast("string"),
        F.col("week_start").cast("date"),
        F.col("is_promoted").cast("boolean"),
    )


@dlt.table(
    name="compliance_results",
    comment="Gold layer: back-to-back promotion violations flagged via UC function",
)
def compliance_results():
    # The UC function is called here exactly as it is in the BDD @when step.
    # If the BDD suite is green, this query is validated.
    return spark.sql(f"""
        WITH timeline_with_lags AS (
            SELECT *,
                LAG(is_promoted, 1) OVER w AS prev_promo_1,
                LAG(is_promoted, 2) OVER w AS prev_promo_2,
                LAG(is_promoted, 3) OVER w AS prev_promo_3,
                LAG(is_promoted, 4) OVER w AS prev_promo_4
            FROM LIVE.silver_timeline
            WINDOW w AS (PARTITION BY product_id, location_id ORDER BY week_start)
        )
        SELECT
            *,
            {CATALOG}.{SCHEMA}.check_back_to_back_promo(
                is_promoted,
                prev_promo_1, prev_promo_2, prev_promo_3, prev_promo_4
            ) AS b2b_violation
        FROM timeline_with_lags
    """)
