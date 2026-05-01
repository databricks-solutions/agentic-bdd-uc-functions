"""behave hooks: load .env and validate required env vars before any test runs."""

from __future__ import annotations

import os
import sys
from pathlib import Path


REQUIRED = ["DATABRICKS_WAREHOUSE_ID"]


def _load_dotenv() -> None:
    env_file = Path(__file__).resolve().parents[2] / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def before_all(context) -> None:
    _load_dotenv()
    missing = [v for v in REQUIRED if not os.environ.get(v)]
    if missing:
        sys.stderr.write(
            f"Missing required env vars: {', '.join(missing)}.\n"
            "Copy .env.example to .env and fill in your values.\n"
        )
        sys.exit(2)
