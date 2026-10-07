from backend.app.models.change import Change
from backend.app.schemas.consequence import ConsequenceCreate
from backend.app.engines.consequence_rules import (
    ConsequenceRule,
    DETERMINISTIC_RULES,
)


class DeterministicConsequenceEngine:
    """Evaluate deterministic consequence rules for an enterprise change."""

    def __init__(
        self,
        rules: tuple[ConsequenceRule, ...] = DETERMINISTIC_RULES,
    ):
        self.rules = rules

    def analyze(self, change: Change) -> list[ConsequenceCreate]:
        consequences: list[ConsequenceCreate] = []

        for rule in self.rules:
            if not rule.applies_to(change):
                continue

            consequence = rule.evaluate(change)

            if consequence is not None:
                consequences.append(consequence)

        return consequences

    def analyze_with_rule_ids(
        self,
        change: Change,
    ) -> list[tuple[str, ConsequenceCreate]]:
        results: list[tuple[str, ConsequenceCreate]] = []

        for rule in self.rules:
            if not rule.applies_to(change):
                continue

            consequence = rule.evaluate(change)

            if consequence is not None:
                results.append((rule.rule_id, consequence))

        return results