from healthcare_reliability_utils import (
    ReliabilityConfig,
    load_patient_document,
    patient_source_rows,
    run_reliability_agent,
    scorecard,
    transform_patient_context,
)


def test_patient_fixture_is_loaded_from_a_mock_document():
    document = load_patient_document()
    assert document["path"].endswith("patient_records/synthetic_transition_record.md")
    assert document["classification"] == "Synthetic PHI"
    assert document["direct_identifiers"]["MRN"] == "HLS-88421"
    assert "congestive heart failure" in document["clinical_note"]
    assert patient_source_rows()[0]["used_by"] == (
        "transform_patient_context, get_patient_summary"
    )


def test_preprocessing_exposes_only_purpose_limited_context():
    transformed = transform_patient_context(
        "minimum_necessary",
        ["patient_record:deidentify"],
    )
    document = load_patient_document()
    assert "heart failure" in transformed
    assert all(
        value not in transformed for value in document["direct_identifiers"].values()
    )


def test_preprocessing_requires_its_own_patient_scope():
    try:
        transform_patient_context("minimum_necessary", [])
    except PermissionError:
        return
    raise AssertionError("Patient preprocessing should fail without de-identification scope")


def test_patient_tool_reads_the_mock_document():
    result = run_reliability_agent(ReliabilityConfig.broken())
    assert load_patient_document()["clinical_note"] in result["tool_result"]["value"]


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
