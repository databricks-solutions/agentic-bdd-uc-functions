# agentic-bdd-uc-functions

End-to-end example of BDD testing for Databricks Unity Catalog functions, using [Behave](https://behave.readthedocs.io/) and the [Statement Execution API](https://docs.databricks.com/api/workspace/statementexecution).

Tests run on a standard CI runner (GitHub Actions) — no Spark session, no local cluster, no Java. Each scenario is one HTTP call to a real UC function.

> **Status:** community-contributed reference implementation. Not officially supported by Databricks. Issues and PRs are welcome but response times are best-effort. Use at your own risk; review the code against your own security and compliance requirements before using in production.

📖 **[Read the deep dive blog post →](docs/blog.md)** — the why behind this pattern, where it fits, and where it doesn't.

## How it works

A Unity Catalog SQL function is the single source of truth for the business rule. Both callers reference it without duplication:

```
UC function (sql/)
    ├── BDD test suite (tests/bdd/)   — validates the contract via Statement Execution API
    └── Lakeflow SDP pipeline (pipelines/)  — calls the same function in production
```

The BDD suite gates pipeline promotion in CI. If a code change breaks a scenario, the pipeline never runs.

## Prerequisites

- Databricks workspace with Unity Catalog enabled
- A running SQL warehouse (Serverless recommended)
- Python 3.10+, [`uv`](https://docs.astral.sh/uv/), [Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html) (Go-based, v0.200+)

Verify CLI auth before starting:

```bash
databricks current-user me
```

## Project structure

```
databricks-bdd/
├── src/
│   └── compliance_bdd/         # Python package — BDD utilities
│       ├── spark_rules.py       # Statement Execution API wrapper
│       └── fixtures.py          # Domain → UC function argument translators
│
├── pipelines/
│   └── compliance_pipeline.py  # Lakeflow SDP source file (workspace artifact, not packaged)
│
├── sql/
│   └── check_back_to_back_promo.sql  # UC function definition — the shared contract
│
├── scripts/
│   └── deploy_function.py      # Deploys UC function to target catalog/schema
│
├── tests/
│   └── bdd/
│       ├── environment.py       # behave hooks (.env loading, env var validation)
│       ├── features/
│       │   └── *.feature        # Gherkin scenarios — human-readable rule contracts
│       └── steps/
│           └── *_steps.py       # Step definitions — thin wiring between Gherkin and call_rule()
│
├── resources/
│   ├── pipeline.yml             # DABs pipeline resource (Lakeflow SDP)
│   └── jobs.yml                 # DABs job resources
│
├── .github/
│   └── workflows/
│       └── bdd.yml              # CI: bundle deploy → BDD tests (gate) → pipeline run
│
├── databricks.yml               # Asset Bundle config with dev/staging/prod targets
├── pyproject.toml               # Python project — packages src/ only
├── behave.ini                   # behave configuration
└── Makefile                     # Command interface
```

### Why `src/` layout?

The `src/compliance_bdd/` package is the only thing that gets built into a wheel and deployed as a library dependency. The `pipelines/` directory contains Lakeflow SDP source files that the pipeline runtime discovers and executes directly — they can't be installed as a package entry point. Keeping them separate makes the distinction explicit and prevents `setuptools` from accidentally packaging workspace artifacts.

See `pyproject.toml`:

```toml
[tool.setuptools.packages.find]
where = ["src"]  # only package src/ — pipelines/ stays out of the wheel
```

## Quick start

```bash
# 1. Clone and install
git clone https://github.com/you/databricks-bdd
cd databricks-bdd
cp .env.example .env          # fill in DATABRICKS_WAREHOUSE_ID and target catalog/schema
make install

# 2. Deploy the UC function
make setup

# 3. Run the BDD suite
make test
```

Expected output on a warm warehouse:

```
Feature: Back-to-Back Promotion Compliance
  Rule: Products must have a minimum 4-week gap between promotions

.........  9 scenarios (9 passed)
Took 0m14.2s
```

## Databricks Asset Bundle integration

The bundle has three targets. `BDD_CATALOG` and `BDD_SCHEMA` are driven by bundle variables — the test suite always points at the same catalog/schema as the deployed pipeline.

| Target | Catalog | Schema |
|--------|---------|--------|
| `dev` | `dev` | `compliance_<your-username>` |
| `staging` | `staging` | `compliance_staging` |
| `prod` | `main` | `compliance` |

```bash
# Validate the bundle config
make validate

# Deploy to your personal dev schema
make deploy-dev

# Deploy to staging (what CI does)
make deploy-staging
```

### CI/CD sequence

On push to `main`, the workflow enforces a strict gate sequence:

```
bundle deploy --target staging
    ↓  deploys UC function + pipeline definition

behave (BDD gate)
    ↓  calls real UC functions in staging catalog
    ↓  green → proceed  |  red → stop

bundle run compliance_pipeline --target staging
    ↓  pipeline runs against validated functions
```

On pull requests: deploy + BDD only (pipeline run is skipped).

## GitHub Actions setup

Add these secrets to your repository (`Settings → Secrets and variables → Actions`):

| Secret | Value |
|--------|-------|
| `DATABRICKS_HOST` | Your workspace URL, e.g. `https://adb-xxx.azuredatabricks.net` |
| `DATABRICKS_TOKEN` | Service principal PAT (not a personal token) |
| `DATABRICKS_WAREHOUSE_ID` | SQL warehouse ID from the Connection Details tab |

Grant the service principal: `USE CATALOG`, `USE SCHEMA`, `EXECUTE` on the target schemas, and `CAN_USE` on the warehouse.

## Adding a new rule

1. Write the SQL function in `sql/` and deploy it with `make setup`
2. Create `tests/bdd/features/<rule_name>.feature` with Gherkin scenarios
3. Add a fixture translator in `src/compliance_bdd/fixtures.py` if the function has a non-trivial argument shape
4. Add step definitions in `tests/bdd/steps/<rule_name>_steps.py`
5. Run `make test`

The production pipeline calls the same UC function — add it to `pipelines/compliance_pipeline.py` and it's covered by the existing BDD gate.

## Cost

Each scenario is one warehouse query. The suite runs 9 scenarios — negligible at Serverless SQL pricing. A Scenario Outline with hundreds of rows adds up on a busy PR queue; consider batching via `VALUES` clauses if cost becomes a concern.
