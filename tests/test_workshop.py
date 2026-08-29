from workshop_utils import (
    ScenarioConfig,
    comparison_rows,
    expected_failure_evidence,
    phi_findings,
    run_agent,
)


def test_broken_trace_contains_intended_failures():
    result = run_agent(ScenarioConfig.broken())
    assert {row["failure"] for row in expected_failure_evidence()} == {
        "Poisoning",
        "Distraction",
        "Confusion",
        "Clash",
    }
    assert {row["location"] for row in phi_findings(result)} == {
        "retrieval",
        "tool_output",
        "model_context",
        "memory",
    }
    assert result["selected_tool"] == "get_patient_summary"


def test_fixed_trace_protects_boundaries_and_improves_routing():
    result = run_agent(ScenarioConfig.fixed())
    assert phi_findings(result) == []
    assert result["selected_tool"] == "search_clinical_policy"
    assert "within 7 days" in result["answer"]
    assert "no patient facts retained" in result["memory"]


def test_comparison_is_decision_ready():
    rows = comparison_rows(run_agent(ScenarioConfig.broken()), run_agent(ScenarioConfig.fixed()))
    by_check = {row["check"]: row for row in rows}
    assert by_check["PHI locations"] == {"check": "PHI locations", "broken": 4, "fixed": 0}
    assert by_check["Safe memory"]["fixed"] is True

