# Demo specification

## Audience and outcome

Mixed technical healthcare AI practitioners learn to follow context through MLflow spans, locate
synthetic PHI exposure, distinguish poisoning/distraction/confusion/clash, and validate retrieval,
tool-routing, and memory remediations using before/after evidence.

## Architecture

Databricks source notebooks call a small synthetic Python agent instrumented with MLflow tracing.
The agent uses embedded fixtures and deterministic routing so failures are reproducible. An optional
Databricks-hosted Claude call sits behind a fallback. No external data or persistent infrastructure
is required.

## Safety and visual language

Use plain Databricks notebook markdown, concise tables, and explicit synthetic-data warnings.
Never introduce real identifiers or medical records. Baseline traces intentionally contain only the
fictional markers defined in `workshop_utils.py`.

