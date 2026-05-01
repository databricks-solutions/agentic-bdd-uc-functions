"""Thin wrapper around the Databricks Statement Execution API.

Calls real Unity Catalog functions over HTTP — no Spark session, no local
cluster, no Java. Each call_rule() invocation is one synchronous warehouse
query that returns the boolean result of the UC function.
"""

from __future__ import annotations

import os
from functools import lru_cache

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState


@lru_cache(maxsize=1)
def _client() -> WorkspaceClient:
    # lru_cache prevents a new OAuth exchange on every scenario (~300ms each).
    profile = os.environ.get("DATABRICKS_PROFILE", "DEFAULT")
    return WorkspaceClient(profile=profile)


def call_rule(expr: str) -> bool:
    """Execute `SELECT <catalog>.<schema>.<expr>` and return the boolean result."""
    warehouse_id = os.environ["DATABRICKS_WAREHOUSE_ID"]
    catalog = os.environ.get("BDD_CATALOG", "main")
    schema = os.environ.get("BDD_SCHEMA", "compliance")

    response = _client().statement_execution.execute_statement(
        warehouse_id=warehouse_id,
        statement=f"SELECT {catalog}.{schema}.{expr}",
        wait_timeout="30s",
    )
    if response.status.state != StatementState.SUCCEEDED:
        raise RuntimeError(f"Statement failed: {response.status.error}")

    return str(response.result.data_array[0][0]).lower() == "true"
