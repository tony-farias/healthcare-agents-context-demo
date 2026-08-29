from healthcare_reliability_utils import ReliabilityConfig, run_reliability_agent, scorecard


def test_four_run_matrix():
    results = [
        run_reliability_agent(config)
        for config in [
            ReliabilityConfig.broken(),
            ReliabilityConfig.over_redacted(),
            ReliabilityConfig.accurate_unsafe(),
            ReliabilityConfig.governed(),
        ]
    ]
    rows = scorecard(results)
    assert [(r["accuracy_pass"], r["privacy_pass"]) for r in rows] == [
        (False, False),
        (False, True),
        (True, False),
        (True, True),
    ]
    assert rows[-1]["selected_tool"] == "search_clinical_policy"
    assert rows[-1]["retrieved_policies"] == "CP-104"
