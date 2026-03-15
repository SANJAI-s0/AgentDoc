from apps.agents.schemas import ValidationOutput


def test_validation_output_schema_accepts_expected_payload():
    payload = ValidationOutput(
        document_id="doc_123",
        overall_status="approved",
        risk_score=0.12,
        checks=[],
        next_action="route",
        reasons=["All checks passed."],
    )
    assert payload.document_id == "doc_123"
    assert payload.overall_status == "approved"
