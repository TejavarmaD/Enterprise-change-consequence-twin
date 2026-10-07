# Phase 1 — Enterprise Data Model

## Purpose

Phase 1 establishes the relational foundation of the Enterprise Change
Consequence Twin (ECCT).

The goal is to represent the core enterprise entities that ECCT will
eventually use for consequence analysis, evidence gathering, dependency
analysis, risk assessment, and decision support.

## Implemented Entity Model

The current ECCT database contains 18 ORM entities:

1. System
2. Service
3. API
4. Database
5. Data Asset
6. Data Pipeline
7. ML Model
8. Business Rule
9. Business Process
10. Policy
11. Metric
12. Team
13. Test
14. Deployment
15. Incident
16. Document
17. Change
18. Consequence Assessment

## Change

A `Change` represents a proposed enterprise change that ECCT may analyze.

Current fields include:

- id
- change_id
- change_type
- title
- description
- target_entity_type
- target_entity_id
- current_state
- proposed_state
- affected_domain
- requester
- business_reason
- expected_effect
- constraints
- uncertainty

`change_id` is unique and provides an external identifier for the change.

## Consequence Assessment

A `ConsequenceAssessment` represents a consequence identified for a
specific change.

Current fields include:

- id
- change_id
- consequence_category
- consequence_type
- description
- evidence_classification
- probability
- impact
- risk_score
- confidence
- evidence
- unknowns
- recommended_test
- approval_required

## Implemented Relationship

The current ORM model explicitly implements:

```text
Change
  └── has many → ConsequenceAssessment