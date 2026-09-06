# Databricks notebook source
# MAGIC %md
# MAGIC # Instructor guide and answer key
# MAGIC
# MAGIC ## 45-minute run of show
# MAGIC
# MAGIC - 0–3: setup and synthetic-data warning
# MAGIC - 3–10: trace-reading primer and four failure modes
# MAGIC - 10–15: generate the broken trace
# MAGIC - 15–25: participant trace triage
# MAGIC - 25–32: apply remediation profile
# MAGIC - 32–39: compare traces
# MAGIC - 39–45: debrief and exit check
# MAGIC
# MAGIC ## Expected findings
# MAGIC
# MAGIC - PHI first appears in `retrieve_context`, appears again in `tool_call`, reaches `model`,
# MAGIC   and is persisted by `memory_write`.
# MAGIC - `patient-note-88421` is poisoning; `policy-giant-chunk` is distracting and mixes two active,
# MAGIC   authoritative standards: CP-104 requires 7 days while CM-220 requires 30 days. The selected
# MAGIC   patient tool also says 30 days, and no retrieved precedence rule resolves the conflict.
# MAGIC - Identical broken tool descriptions cause clash; progressive disclosure removes the
# MAGIC   patient-record tool from a policy-only task.
# MAGIC - Output redaction is too late: PHI has already reached inference and tracing, and raw memory
# MAGIC   can retain it. The fixed flow filters retrieval, guards context, and summarizes memory.
# MAGIC
# MAGIC ## Facilitation notes
# MAGIC
# MAGIC Keep `LIVE_MODEL=False` for timing predictability. In the optional live-model run, the broken
# MAGIC prompt requires the model to identify the unresolved active-policy conflict rather than use
# MAGIC outside clinical knowledge to silently select seven days.
# MAGIC Remind participants that baseline PHI is synthetic; real systems should avoid logging raw PHI.