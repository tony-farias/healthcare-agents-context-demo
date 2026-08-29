# Context Engineering for Healthcare AI Agents

A 45-minute, hands-on Databricks workshop for diagnosing and tuning healthcare agents from
MLflow traces. All patient-like values are fictional markers created solely for the lab.

## Participant path

Run the notebooks in numeric order. Use serverless compute and keep `LIVE_MODEL=False` for fully
deterministic results. Set it to `True` only if `databricks-claude-sonnet-4-5` is available; the
agent falls back automatically if the endpoint cannot be called.

The combined lab generates a broken and fixed trace. Open each trace from the notebook's MLflow
panel and inspect retrieval, context guard, tool routing, model, and memory spans.

## Free Edition import

Download or clone this directory, import the `notebooks` folder into a Databricks workspace, and
attach serverless compute. The lab does not require Unity Catalog objects, Vector Search, DBFS,
secrets, external data, or a paid model endpoint.

## Local validation

```bash
uv sync --dev
uv run pytest
uv run ruff check .
```

## Deployment

Authenticate the `fe-vm-hls-amer` profile, then sync the portable content:

```bash
databricks sync . /Shared/context-engineering-healthcare-agents --profile fe-vm-hls-amer
```

