import pytest
from pydantic import ValidationError

from backend.app.schemas.change import ChangeCreate
from backend.app.schemas.consequence import ConsequenceCreate


def test_change_create_accepts_valid_data():
    change = ChangeCreate(
        change_id="CHG-001",
        change_type="business_rule",
        title="Update customer eligibility",
        description="Increase the minimum eligible customer age.",
        target_entity_type="business_rule",
        target_entity_id=1,
    )

    assert change.change_id == "CHG-001"
    assert change.target_entity_id == 1


def test_change_create_rejects_invalid_target_entity_id():
    with pytest.raises(ValidationError):
        ChangeCreate(
            change_id="CHG-001",
            change_type="business_rule",
            title="Update customer eligibility",
            description="Increase the minimum eligible customer age.",
            target_entity_type="business_rule",
            target_entity_id=0,
        )


def test_change_create_rejects_empty_required_fields():
    with pytest.raises(ValidationError):
        ChangeCreate(
            change_id="",
            change_type="business_rule",
            title="Update customer eligibility",
            description="Increase the minimum eligible customer age.",
            target_entity_type="business_rule",
            target_entity_id=1,
        )


def test_consequence_create_accepts_valid_probability_and_impact():
    consequence = ConsequenceCreate(
        consequence_category="business",
        consequence_type="customer_eligibility",
        description="Some customers may become ineligible.",
        evidence_classification="PREDICTION",
        probability=0.8,
        impact=0.7,
        risk_score=0.56,
        confidence=0.9,
    )

    assert consequence.probability == 0.8
    assert consequence.impact == 0.7
    assert consequence.risk_score == 0.56
    assert consequence.confidence == 0.9


@pytest.mark.parametrize(
    "field",
    ["probability", "impact", "risk_score", "confidence"],
)
def test_consequence_create_rejects_values_above_one(field):
    values = {
        "consequence_category": "technical",
        "consequence_type": "dependency_failure",
        "description": "A dependent service may fail.",
        "evidence_classification": "PREDICTION",
        field: 1.01,
    }

    with pytest.raises(ValidationError):
        ConsequenceCreate(**values)


@pytest.mark.parametrize(
    "field",
    ["probability", "impact", "risk_score", "confidence"],
)
def test_consequence_create_rejects_negative_values(field):
    values = {
        "consequence_category": "technical",
        "consequence_type": "dependency_failure",
        "description": "A dependent service may fail.",
        "evidence_classification": "PREDICTION",
        field: -0.01,
    }

    with pytest.raises(ValidationError):
        ConsequenceCreate(**values)