# Databricks notebook source
# MAGIC %md
# MAGIC # Read a trace like a context engineer (7 minutes)
# MAGIC
# MAGIC Start at the root agent span, then follow context in order:
# MAGIC
# MAGIC 1. **Retrieval** — what entered, and was it authorized and relevant?
# MAGIC 2. **Context guard** — what was dropped, transformed, or allowed through?
# MAGIC 3. **Tool routing/output** — which capability was exposed and what data returned?
# MAGIC 4. **Model** — what context actually reached inference?
# MAGIC 5. **Memory** — what was persisted after the response?

# COMMAND ----------

from workshop_utils import ScenarioConfig, expected_failure_evidence, run_agent

# COMMAND ----------

primer_result = run_agent(ScenarioConfig.broken())
print("Generated one deliberately broken MLflow trace.")
display(expected_failure_evidence())

# COMMAND ----------

# MAGIC %md
# MAGIC ### Four context failure modes
# MAGIC
# MAGIC - **Poisoning:** untrusted context tries to alter agent behavior.
# MAGIC - **Distraction:** irrelevant volume crowds out the useful signal.
# MAGIC - **Confusion:** stale or mixed evidence makes the answer uncertain.
# MAGIC - **Clash:** overlapping instructions or tools compete.
# MAGIC
# MAGIC Open the trace and locate one span for each. Do not start with the final answer—the first bad span is usually the better intervention point.