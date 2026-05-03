# Contributing

Thanks for considering a contribution. This repo is a reference implementation for BDD testing of Unity Catalog SQL functions on Databricks. Contributions that extend the pattern, add real-world examples, or improve developer experience are welcome.

## Ground rules

- **Keep examples runnable end-to-end.** A new example feature file or rule should come with the SQL function, the step definitions, and the fixture translator — not just a feature file.
- **Don't add real customer data.** All examples should use synthetic data generated at runtime. The fixtures pattern in `src/compliance_bdd/fixtures.py` is the model.
- **Match the existing terseness.** Step definitions stay thin. Comments only when the *why* is non-obvious.
- **No proprietary code.** This repo is licensed under the [Databricks DB License](LICENSE.md). Anything contributed is licensed under those terms.

## Development workflow

```bash
# 1. Fork and clone
git clone https://github.com/<your-fork>/agentic-bdd-uc-functions
cd agentic-bdd-uc-functions

# 2. Install dependencies
uv sync

# 3. Configure your workspace
cp .env.example .env
# fill in DATABRICKS_WAREHOUSE_ID, BDD_CATALOG, BDD_SCHEMA

# 4. Deploy the UC function and run tests
make setup
make test
```

## Adding a new rule

1. Create the SQL function in `sql/<rule_name>.sql`
2. Update `scripts/deploy_function.py` (or generalize it) to deploy the new function
3. Write the Gherkin scenarios in `tests/bdd/features/<rule_name>.feature` — start with a small set authored by the domain expert (your "golden set")
4. Add the fixture in `src/compliance_bdd/fixtures.py` if the function's argument shape is non-trivial
5. Add step definitions in `tests/bdd/steps/<rule_name>_steps.py`
6. Run `make test` and ensure all scenarios pass

## Pull request checklist

- [ ] Tests pass locally (`make test`)
- [ ] Bundle validates (`make validate`)
- [ ] No secrets, tokens, or workspace URLs in the diff
- [ ] New rules include both feature file and step definitions
- [ ] README updated if the new rule needs documentation

## Reporting issues

For bugs or feature requests, open a GitHub issue with:
- What you expected to happen
- What actually happened
- A minimal reproduction (Gherkin + SQL function if relevant)
- Your Databricks workspace region and warehouse type

## Questions

Open a GitHub discussion or reach out via the contact info in the repo profile.
