from backend.app.engines.deterministic_consequence_engine import (
    DeterministicConsequenceEngine,
)
from backend.app.models.change import Change


def make_change(**overrides) -> Change:
    values = {
        "change_id": "CHG-ENGINE-001",
        "change_type": "business rule",
        "title": "Update enterprise component",
        "description": "Apply a requested enterprise configuration change.",
        "target_entity_type": "BusinessRule",
        "target_entity_id": 1,
        "current_state": "Current configuration is active.",
        "proposed_state": "Updated configuration is active.",
        "affected_domain": "Customer eligibility",
        "requester": "Test User",
        "business_reason": "Operational improvement.",
        "expected_effect": "Improve the target process.",
        "constraints": None,
        "uncertainty": None,
    }

    values.update(overrides)

    return Change(**values)


def test_eligibility_change_produces_business_and_semantic_consequences():
    engine = DeterministicConsequenceEngine()

    change = make_change(
        change_type="business rule",
        title="Change customer eligibility",
        description="Change eligibility threshold from 18 to 21.",
    )

    consequences = engine.analyze(change)

    categories = {item.consequence_category for item in consequences}

    assert categories == {"Business", "Semantic"}
    assert len(consequences) == 2


def test_api_change_produces_technical_consequence():
    engine = DeterministicConsequenceEngine()

    change = make_change(
        change_type="API",
        title="Change customer API contract",
        description="Add a required field to the customer API.",
    )

    consequences = engine.analyze(change)

    assert len(consequences) == 1
    assert consequences[0].consequence_category == "Technical"
    assert consequences[0].consequence_type == "API compatibility risk"


def test_schema_change_produces_data_consequence():
    engine = DeterministicConsequenceEngine()

    change = make_change(
        change_type="schema",
        title="Change customer database schema",
        description="Rename customer_status column.",
    )

    consequences = engine.analyze(change)

    assert len(consequences) == 1
    assert consequences[0].consequence_category == "Data"
    assert consequences[0].consequence_type == "Schema compatibility risk"


def test_model_change_produces_model_consequence():
    engine = DeterministicConsequenceEngine()

    change = make_change(
        change_type="ML model",
        title="Replace customer risk model",
        description="Deploy a new customer risk model.",
    )

    consequences = engine.analyze(change)

    assert len(consequences) == 1
    assert consequences[0].consequence_category == "Model"


def test_unrecognized_change_produces_no_consequences():
    engine = DeterministicConsequenceEngine()

    change = make_change(
        change_type="documentation",
        title="Update internal documentation",
        description="Fix a spelling mistake.",
    )

    consequences = engine.analyze(change)

    assert consequences == []


def test_rule_ids_are_available_for_auditability():
    engine = DeterministicConsequenceEngine()

    change = make_change(
        change_type="API",
        title="Change customer API",
        description="Change API contract.",
    )

    results = engine.analyze_with_rule_ids(change)

    assert len(results) == 1
    rule_id, consequence = results[0]

    assert rule_id == "API-TECHNICAL-001"
    assert consequence.consequence_category == "Technical"


def test_multiple_rules_can_fire_for_one_change():
    engine = DeterministicConsequenceEngine()

    change = make_change(
        change_type="business rule",
        title="Change customer eligibility",
        description="Change eligibility threshold from 18 to 21.",
    )

    results = engine.analyze_with_rule_ids(change)

    rule_ids = {rule_id for rule_id, _ in results}

    assert rule_ids == {
        "ELIGIBILITY-BUSINESS-001",
        "ELIGIBILITY-SEMANTIC-001",
    }

def test_api_change_with_eligibility_word_does_not_trigger_eligibility_rules():
    engine = DeterministicConsequenceEngine()

    change = make_change(
        change_type="API",
        title="Change customer eligibility API",
        description="Expose the existing eligibility status through the API.",
    )

    results = engine.analyze_with_rule_ids(change)

    rule_ids = {rule_id for rule_id, _ in results}

    assert rule_ids == {"API-TECHNICAL-001"}


def test_schema_change_with_eligibility_word_does_not_trigger_eligibility_rules():
    engine = DeterministicConsequenceEngine()

    change = make_change(
        change_type="schema",
        title="Store customer eligibility status",
        description="Add an eligibility_status column to the customer table.",
    )

    results = engine.analyze_with_rule_ids(change)

    rule_ids = {rule_id for rule_id, _ in results}

    assert rule_ids == {"SCHEMA-DATA-001"}


def test_model_change_with_eligibility_word_does_not_trigger_eligibility_rules():
    engine = DeterministicConsequenceEngine()

    change = make_change(
        change_type="ML model",
        title="Improve eligibility prediction model",
        description="Deploy a model used to predict eligibility.",
    )

    results = engine.analyze_with_rule_ids(change)

    rule_ids = {rule_id for rule_id, _ in results}

    assert rule_ids == {"MODEL-BEHAVIOR-001"}


def test_documentation_change_with_business_rule_language_produces_no_consequences():
    engine = DeterministicConsequenceEngine()

    change = make_change(
        change_type="documentation",
        title="Document business rule behavior",
        description="Update documentation describing an existing business rule.",
    )

    results = engine.analyze_with_rule_ids(change)

    assert results == []


def test_generic_business_rule_produces_generic_semantic_consequence():
    engine = DeterministicConsequenceEngine()

    change = make_change(
        change_type="business rule",
        title="Change transaction approval rule",
        description="Transactions above the new threshold require additional approval.",
    )

    results = engine.analyze_with_rule_ids(change)

    rule_ids = {rule_id for rule_id, _ in results}

    assert rule_ids == {"BUSINESS-RULE-SEMANTIC-001"}

def test_same_change_produces_identical_results():
    engine = DeterministicConsequenceEngine()

    change = make_change(
        change_type="business rule",
        title="Change customer eligibility",
        description="Change eligibility threshold from 18 to 21.",
    )

    first_results = engine.analyze_with_rule_ids(change)
    second_results = engine.analyze_with_rule_ids(change)

    assert first_results == second_results