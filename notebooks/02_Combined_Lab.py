# Databricks notebook source
# MAGIC %md
# MAGIC # Combined lab: diagnose and tune (27 minutes)
# MAGIC
# MAGIC **Mission:** determine where synthetic PHI enters the agent, why retrieval underperforms,
# MAGIC and why the wrong tool is selected. Then enable the remediations and prove they worked.
# MAGIC
# MAGIC In the broken live-model run, two active authoritative policies disagree: CP-104 requires
# MAGIC follow-up within 7 days, while CM-220 and the selected patient tool say 30 days. Because no
# MAGIC precedence rule is retrieved, the model should surface an unresolved policy conflict rather
# MAGIC than silently resolving it from outside medical knowledge.

# COMMAND ----------

from workshop_utils import (
    ScenarioConfig,
    comparison_rows,
    phi_findings,
    policy_source_rows,
    run_agent,
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part A — Generate the broken trace (5 minutes)

# COMMAND ----------

try:
    dbutils.widgets.dropdown("live_model", "false", ["false", "true"], "Use hosted model")
    LIVE_MODEL = dbutils.widgets.get("live_model").lower() == "true"
except NameError:
    LIVE_MODEL = False

print("Hosted-model mode:", LIVE_MODEL, "(automatic deterministic fallback remains enabled)")
broken = run_agent(ScenarioConfig.broken(live_model=LIVE_MODEL))
display(phi_findings(broken))
print("Selected tool:", broken["selected_tool"])
print("Answer:", broken["answer"])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Why the broken live model encounters a real policy conflict
# MAGIC
# MAGIC The broken retrieval and tool path supplies three competing signals:
# MAGIC
# MAGIC | Evidence reaching the model | Status | Required follow-up |
# MAGIC |---|---|---:|
# MAGIC | Cardiology Discharge Policy `CP-104` | Active and authoritative | Within **7 days** |
# MAGIC | Care Management Standard `CM-220` | Active and authoritative | Within **30 days** |
# MAGIC | `get_patient_summary` tool output | Selected by the ambiguous router | Within **30 days** |
# MAGIC
# MAGIC Nothing in the retrieved context says whether cardiology policy or care-management policy
# MAGIC has precedence. The model therefore cannot safely derive one controlling interval. The
# MAGIC broken live prompt prevents it from using outside clinical knowledge to break the tie and
# MAGIC asks it to expose the unresolved conflict explicitly.
# MAGIC
# MAGIC This is **context confusion**: the model is not missing information; it has mutually
# MAGIC inconsistent information without the metadata or policy hierarchy needed to resolve it.
# MAGIC A plausible final answer does not repair that upstream defect.
# MAGIC
# MAGIC In the MLflow trace, inspect:
# MAGIC
# MAGIC 1. `retrieve_context` — both active standards appear in the oversized mixed chunk.
# MAGIC 2. `tool_router` — overlapping descriptions expose the wrong patient-record tool.
# MAGIC 3. `tool_call` — the tool independently reinforces the 30-day interval.
# MAGIC 4. `model` — all conflicting evidence reaches inference with no precedence rule.
# MAGIC
# MAGIC The fixed profile resolves the problem before inference: it retrieves only small approved
# MAGIC policy chunks and exposes only the policy-search tool. The resulting context contains one
# MAGIC applicable seven-day standard rather than asking the model to adjudicate organizational policy.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Open the fictional source policies
# MAGIC
# MAGIC These are synthetic workshop documents—not clinical guidance. Their metadata and URIs are
# MAGIC carried into retrieval results and recorded on the `retrieve_context` MLflow span, allowing
# MAGIC participants to trace a model statement back to the exact source and version.
# MAGIC
# MAGIC - [Open CP-104 — Cardiology Discharge Policy](/#workspace/Shared/context-engineering-healthcare-agents/assets/policies/CP-104.pdf)
# MAGIC - [Open CM-220 — Enterprise Care Management Standard](/#workspace/Shared/context-engineering-healthcare-agents/assets/policies/CM-220.pdf)

# COMMAND ----------

display(policy_source_rows())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part B — Trace triage (10 minutes)
# MAGIC
# MAGIC Inspect the new trace and record:
# MAGIC
# MAGIC | Question | Your finding |
# MAGIC |---|---|
# MAGIC | First span containing an identifier or diagnosis | |
# MAGIC | First point where PHI could be stopped before inference | |
# MAGIC | Span showing persisted PHI | |
# MAGIC | Retrieval evidence for poisoning, distraction, and confusion | |
# MAGIC | Why the router selected the patient tool | |
# MAGIC
# MAGIC Choose interventions at the earliest safe boundary—not only at final-answer rendering.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part C — Apply the remediation profile (7 minutes)
# MAGIC
# MAGIC The fixed profile makes five controlled changes: small policy-only chunks, just-in-time
# MAGIC retrieval, a drop/redact guard, progressive tool disclosure, and allowlisted memory.
# MAGIC
# MAGIC ### Is this a real agent run?
# MAGIC
# MAGIC **Yes, with an important qualification.** `run_agent(...)` executes an actual agent-shaped
# MAGIC workflow, and its root agent, retriever, guard, router, tool, model, and memory functions are
# MAGIC instrumented with `mlflow.trace`. In Databricks, each call therefore creates a real nested
# MAGIC MLflow trace that you can open and inspect.
# MAGIC
# MAGIC The workshop uses controlled local fixtures so every participant sees the same failure:
# MAGIC retrieval searches an embedded document list, routing selects from embedded tool definitions,
# MAGIC and the tools return synthetic values. These are executable components, but they are not
# MAGIC production Vector Search, EHR, or MCP integrations.
# MAGIC
# MAGIC The `model` span has two modes:
# MAGIC
# MAGIC - `LIVE_MODEL=True`: calls the `databricks-claude-sonnet-4-5` serving endpoint. If that call
# MAGIC   fails, the workshop records `deterministic_fallback` and continues with the fixed response.
# MAGIC - `LIVE_MODEL=False`: skips the hosted model and deliberately uses deterministic output. The
# MAGIC   workflow and MLflow trace are still real; only the generated answer is simulated.
# MAGIC
# MAGIC `ScenarioConfig.fixed()` does not train or repair a model. It returns a configuration object
# MAGIC that activates five safer branches inside the same agent implementation:
# MAGIC
# MAGIC | Setting | Fixed value | Runtime effect |
# MAGIC |---|---:|---|
# MAGIC | `retrieval_timing` | `just_in_time` | Records task-specific retrieval timing in the trace. |
# MAGIC | `chunk_strategy` | `small_policy_chunks` | Retrieves only small, approved policy chunks; excludes the patient note and giant mixed chunk. |
# MAGIC | `redact_phi` | `True` | Drops unsafe documents and redacts synthetic PHI before inference. |
# MAGIC | `progressive_tool_disclosure` | `True` | Exposes only `search_clinical_policy`, removing the ambiguous patient tool. |
# MAGIC | `safe_memory` | `True` | Persists an allowlisted, de-identified summary instead of the raw transcript. |
# MAGIC
# MAGIC The next two lines first construct that configuration, then execute the complete traced
# MAGIC workflow with it. Compare this trace with the broken trace to see which spans changed.

# COMMAND ----------

fixed_config = ScenarioConfig.fixed(live_model=LIVE_MODEL)
fixed = run_agent(fixed_config)

display(phi_findings(fixed))
print("Selected tool:", fixed["selected_tool"])
print("Answer:", fixed["answer"])
print("Memory:", fixed["memory"])

assert not phi_findings(fixed), "Synthetic PHI still crossed a protected boundary."
assert fixed["selected_tool"] == "search_clinical_policy"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part D — Compare evidence, not impressions (5 minutes)

# COMMAND ----------

display(comparison_rows(broken, fixed))

# COMMAND ----------

# MAGIC %md
# MAGIC In the two traces, confirm that:
# MAGIC
# MAGIC - `retrieve_context` no longer returns the patient record or giant mixed chunk.
# MAGIC - `context_guard` reports `drop_and_redact` and low PHI risk.
# MAGIC - `tool_router` exposes only the policy tool for this intent.
# MAGIC - `model` receives concise, de-identified context.
# MAGIC - `memory_write` stores an allowlisted summary rather than a raw transcript.
