from dataclasses import dataclass
from typing import Callable

from backend.app.models.change import Change
from backend.app.schemas.consequence import ConsequenceCreate


@dataclass(frozen=True)
class ConsequenceRule:
    rule_id: str
    description: str
    applies_to: Callable[[Change], bool]
    evaluate: Callable[[Change], ConsequenceCreate | None]


def _contains_any(value: str | None, terms: tuple[str, ...]) -> bool:
    if not value:
        return False

    normalized = value.lower()

    return any(term in normalized for term in terms)


def _eligibility_change(change: Change) -> bool:
    if _contains_any(
        change.change_type,
        ("eligibility",),
    ):
        return True

    return (
        _contains_any(change.title, ("eligibility",))
        and _contains_any(
            change.description,
            ("change", "threshold", "criteria", "requirement"),
        )
    )


def _evaluate_eligibility_business(change: Change) -> ConsequenceCreate:
    return ConsequenceCreate(
        consequence_category="Business",
        consequence_type="Eligible population impact",
        description=(
            "The proposed eligibility change may alter the population "
            "that qualifies for the affected business process."
        ),
        evidence_classification="INFERENCE",
        probability=0.80,
        impact=0.70,
        risk_score=0.56,
        confidence=0.85,
        evidence=(
            f"Change '{change.change_id}' references an eligibility or "
            "qualification criterion."
        ),
        unknowns=(
            "The actual size and composition of the affected population "
            "cannot be determined without enterprise data."
        ),
        recommended_test=(
            "Compare the eligible population before and after applying "
            "the proposed criterion."
        ),
        approval_required=True,
    )


def _evaluate_eligibility_semantic(change: Change) -> ConsequenceCreate:
    return ConsequenceCreate(
        consequence_category="Semantic",
        consequence_type="Business definition change",
        description=(
            "The proposed eligibility change may alter the business "
            "meaning of who qualifies for the affected process."
        ),
        evidence_classification="INFERENCE",
        probability=0.75,
        impact=0.65,
        risk_score=0.4875,
        confidence=0.82,
        evidence=(
            f"Change '{change.change_id}' modifies or references "
            "eligibility criteria."
        ),
        unknowns=(
            "Downstream systems and documentation using the existing "
            "definition have not yet been inspected."
        ),
        recommended_test=(
            "Review business definitions, downstream rules, and "
            "documentation for consistency with the proposed criterion."
        ),
        approval_required=True,
    )


def _api_change(change: Change) -> bool:
    return _contains_any(
        change.change_type,
        (
            "api",
            "api contract",
            "endpoint",
        ),
    )


def _evaluate_api_technical(change: Change) -> ConsequenceCreate:
    return ConsequenceCreate(
        consequence_category="Technical",
        consequence_type="API compatibility risk",
        description=(
            "An API-related change may affect consumers that depend on "
            "the current interface or contract."
        ),
        evidence_classification="INFERENCE",
        probability=0.70,
        impact=0.75,
        risk_score=0.525,
        confidence=0.80,
        evidence=(
            f"Change '{change.change_id}' is classified as an API-related change."
        ),
        unknowns=(
            "The complete set of downstream API consumers has not yet "
            "been inspected."
        ),
        recommended_test=(
            "Run API contract and backward-compatibility tests against "
            "known consumers."
        ),
        approval_required=True,
    )


def _schema_change(change: Change) -> bool:
    return _contains_any(
        change.change_type,
        (
            "schema",
            "database schema",
            "data schema",
        ),
    )


def _evaluate_schema_data(change: Change) -> ConsequenceCreate:
    return ConsequenceCreate(
        consequence_category="Data",
        consequence_type="Schema compatibility risk",
        description=(
            "A schema change may affect pipelines, consumers, queries, "
            "or data transformations that depend on the current structure."
        ),
        evidence_classification="INFERENCE",
        probability=0.75,
        impact=0.80,
        risk_score=0.60,
        confidence=0.83,
        evidence=(
            f"Change '{change.change_id}' is classified as a schema-related change."
        ),
        unknowns=(
            "Downstream datasets, pipelines, queries, and consumers "
            "have not yet been fully mapped."
        ),
        recommended_test=(
            "Run schema compatibility tests and validate downstream "
            "pipeline and query behavior."
        ),
        approval_required=True,
    )


def _business_rule_change(change: Change) -> bool:
    if not _contains_any(
        change.change_type,
        ("business rule", "business-rule", "rule"),
    ):
        return False

    return not _eligibility_change(change)


def _evaluate_business_rule_semantic(change: Change) -> ConsequenceCreate:
    return ConsequenceCreate(
        consequence_category="Semantic",
        consequence_type="Business rule meaning change",
        description=(
            "Changing a business rule may alter the meaning or behavior "
            "of decisions made by downstream processes."
        ),
        evidence_classification="INFERENCE",
        probability=0.80,
        impact=0.70,
        risk_score=0.56,
        confidence=0.84,
        evidence=(
            f"Change '{change.change_id}' is classified as a business-rule change."
        ),
        unknowns=(
            "Dependent rules, processes, metrics, and documentation "
            "have not yet been fully evaluated."
        ),
        recommended_test=(
            "Run regression tests for dependent business rules and "
            "reconcile affected business metrics."
        ),
        approval_required=True,
    )


def _model_change(change: Change) -> bool:
    return _contains_any(
        change.change_type,
        (
            "model",
            "machine learning",
            "ml model",
            "ai model",
        ),
    )


def _evaluate_model_operational(change: Change) -> ConsequenceCreate:
    return ConsequenceCreate(
        consequence_category="Model",
        consequence_type="Model behavior change",
        description=(
            "A model-related change may alter prediction behavior, "
            "performance, or downstream decisions."
        ),
        evidence_classification="INFERENCE",
        probability=0.70,
        impact=0.80,
        risk_score=0.56,
        confidence=0.78,
        evidence=(
            f"Change '{change.change_id}' is classified as a model-related change."
        ),
        unknowns=(
            "The effect on prediction distributions and model performance "
            "has not yet been measured."
        ),
        recommended_test=(
            "Compare predictions, performance metrics, calibration, "
            "and relevant data distributions before and after the change."
        ),
        approval_required=True,
    )


DETERMINISTIC_RULES: tuple[ConsequenceRule, ...] = (
    ConsequenceRule(
        rule_id="ELIGIBILITY-BUSINESS-001",
        description="Detect business impact from eligibility changes.",
        applies_to=_eligibility_change,
        evaluate=_evaluate_eligibility_business,
    ),
    ConsequenceRule(
        rule_id="ELIGIBILITY-SEMANTIC-001",
        description="Detect semantic impact from eligibility changes.",
        applies_to=_eligibility_change,
        evaluate=_evaluate_eligibility_semantic,
    ),
    ConsequenceRule(
        rule_id="API-TECHNICAL-001",
        description="Detect API compatibility consequences.",
        applies_to=_api_change,
        evaluate=_evaluate_api_technical,
    ),
    ConsequenceRule(
        rule_id="SCHEMA-DATA-001",
        description="Detect data consequences from schema changes.",
        applies_to=_schema_change,
        evaluate=_evaluate_schema_data,
    ),
    ConsequenceRule(
        rule_id="BUSINESS-RULE-SEMANTIC-001",
        description="Detect semantic consequences from business-rule changes.",
        applies_to=_business_rule_change,
        evaluate=_evaluate_business_rule_semantic,
    ),
    ConsequenceRule(
        rule_id="MODEL-BEHAVIOR-001",
        description="Detect model behavior consequences.",
        applies_to=_model_change,
        evaluate=_evaluate_model_operational,
    ),
)