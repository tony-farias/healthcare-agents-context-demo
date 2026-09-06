# Databricks notebook source
# MAGIC %md
# MAGIC # Before/after debrief (6 minutes)

# COMMAND ----------

from workshop_utils import ScenarioConfig, comparison_rows, run_agent

# COMMAND ----------

broken = run_agent(ScenarioConfig.broken())
fixed = run_agent(ScenarioConfig.fixed())
display(comparison_rows(broken, fixed))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Exit check
# MAGIC
# MAGIC 1. Why is output-only redaction insufficient?
# MAGIC 2. When should generic safety context be preloaded rather than retrieved just in time?
# MAGIC 3. How does progressive disclosure reduce tool clash?
# MAGIC 4. Which trace evidence proves that the fix changed the system rather than merely changing one answer?
# MAGIC
# MAGIC **Transfer rule:** trace the complete context lifecycle—source, transformation, inference,
# MAGIC and persistence—and intervene at the earliest boundary that can enforce the policy.