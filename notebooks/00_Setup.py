# Databricks notebook source
# MAGIC %md
# MAGIC # Context Engineering for Healthcare AI Agents
# MAGIC ## Setup (3 minutes)
# MAGIC
# MAGIC This workshop uses **fictional patient markers only**. Never paste real patient data into these notebooks or MLflow traces.
# MAGIC
# MAGIC The lab creates real nested MLflow traces. If the hosted model is unavailable, a deterministic fallback preserves the same trace structure and intended failures.

# COMMAND ----------

import mlflow

from workshop_utils import ScenarioConfig, SYNTHETIC_PHI

print(f"MLflow version: {mlflow.__version__}")
print("Synthetic markers:", SYNTHETIC_PHI)
assert tuple(int(x) for x in mlflow.__version__.split(".")[:2]) >= (3, 1), (
    "This workshop requires MLflow 3.1+. Attach a current serverless environment or run "
    "%pip install --upgrade 'mlflow[databricks]>=3.1' and restart Python."
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Inference mode
# MAGIC
# MAGIC Leave this `False` for guaranteed, repeatable workshop results. Set it to `True` to call
# MAGIC `databricks-claude-sonnet-4-5`; failures automatically fall back to deterministic output.

# COMMAND ----------

LIVE_MODEL = False
BROKEN_CONFIG = ScenarioConfig.broken(live_model=LIVE_MODEL)
FIXED_CONFIG = ScenarioConfig.fixed(live_model=LIVE_MODEL)

print("Ready. Continue to 01_Trace_Reading_Primer.")

