from pathlib import Path

from healthcare_reliability_utils import (
    ReliabilityConfig,
    as_retrieved_context,
    load_patient_document,
    patient_source_rows,
    run_reliability_agent,
    scorecard,
    transform_patient_context,
)


def test_notebook_uses_unambiguous_mlflow_assessment_and_retrieval_output():
    notebook = (
        Path(__file__).resolve().parents[1]
        / "notebooks"
        / "Accuracy_PHISafety_Combined_Lab.py"
    ).read_text(encoding="utf-8")

    assert 'name="groundedness"' not in notebook
    assert 'name="policy_groundedness"' in notebook
    assert (
        'TESTED_FALLBACK_JUDGE_MODEL = '
        '"databricks:/databricks-qwen3-next-80b-a3b-instruct"'
        in notebook
    )
    assert 'dbutils.widgets.text("judge_model", DEFAULT_JUDGE_MODEL)' in notebook
    assert '"retrieved_context": as_retrieved_context(result["policies"])' in notebook
    assert 'os.environ["MLFLOW_GENAI_EVAL_MAX_WORKERS"] = "1"' in notebook
    assert 'os.environ["MLFLOW_GENAI_EVAL_MAX_SCORER_WORKERS"] = "1"' in notebook


def test_retrieved_context_uses_mlflow_contract():
    result = run_reliability_agent(ReliabilityConfig.governed())
    retrieved_context = as_retrieved_context(result["policies"])

    assert retrieved_context == [
        {
            "content": (
                "Heart-failure discharge requires follow-up within 7 days and "
                "daily weight monitoring."
            ),
            "doc_uri": (
                "/#workspace/Shared/context-engineering-healthcare-agents/notebooks/"
                "policies/CP-104.md"
            ),
        }
    ]
    assert result["policies"][0]["metadata"]["doc_uri"] == retrieved_context[0]["doc_uri"]


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
