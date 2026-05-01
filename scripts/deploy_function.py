"""Deploy the UC SQL function to the target catalog and schema.

Reads catalog/schema from environment variables so it works identically
for local dev (via .env) and CI (via workflow env vars).

Usage:
    uv run python -m scripts.deploy_function
"""

from __future__ import annotations

import os
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState


def _client() -> WorkspaceClient:
    profile = os.environ.get("DATABRICKS_PROFILE", "DEFAULT")
    return WorkspaceClient(profile=profile)


def _execute(client: WorkspaceClient, warehouse_id: str, statement: str) -> None:
    response = client.statement_execution.execute_statement(
        warehouse_id=warehouse_id,
        statement=statement,
        wait_timeout="30s",
    )
    if response.status.state != StatementState.SUCCEEDED:
        raise RuntimeError(f"Statement failed: {response.status.error}")


def deploy() -> None:
    warehouse_id = os.environ["DATABRICKS_WAREHOUSE_ID"]
    catalog = os.environ.get("BDD_CATALOG", "main")
    schema = os.environ.get("BDD_SCHEMA", "compliance")
    client = _client()

    _execute(client, warehouse_id, f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")

    sql = (Path(__file__).parents[1] / "sql" / "check_back_to_back_promo.sql").read_text()
    sql = sql.replace("${catalog}", catalog).replace("${schema}", schema)
    _execute(client, warehouse_id, sql)

    print(f"Deployed check_back_to_back_promo to {catalog}.{schema}")


if __name__ == "__main__":
    deploy()
