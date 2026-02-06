# Peng – Implementation Repo

This is the implementation repo for Peng. The specification lives in
[Peng-spec](https://github.com/monsharen/Peng-spec).

## Architecture

- `src/` – Source code
- `tests/steps/` – Behave step definitions (maps Gherkin → implementation)
- `behave.ini` – Test runner config

## Spec-driven development

All features are specified as Gherkin `.feature` files in the peng-spec repo.
When spec changes land on main, an agent automatically:

1. Analyzes the spec diff
2. Implements changes in this repo
3. Runs the Gherkin tests
4. Creates a PR if tests pass

## Running tests locally

```bash
pip install behave
behave ../peng-spec/features/
```

## Conventions

- Commits reference intent IDs: `feat(intent-feature-NNN): description`
- Step definitions live in `tests/steps/step_<feature-name>.py`
- One step file per feature file
