# ECCT Domain Model

## 1. Purpose

The Enterprise Change Consequence Twin (ECCT) models enterprise entities and their relationships so that the system can analyze the consequences of proposed changes.

ECCT is a decision-support system. It does not automatically deploy changes or replace human approval.

---

## 2. Core Enterprise Entities

### System
A logical enterprise application or platform.

Examples:
- Customer Platform
- Payment Platform
- CRM

### Service
A deployable or independently managed service belonging to a system.

### API
An interface exposed or consumed by a service.

### Database
A persistent data store used by one or more services or pipelines.

### Data Asset
A meaningful dataset, table, topic, file, or business data product.

### Data Pipeline
A process that transforms, transports, validates, or publishes data.

### ML Model
A machine-learning or AI model used by an enterprise process or service.

### Business Rule
A rule that determines business behavior or eligibility.

### Business Process
A business workflow involving systems, services, people, or rules.

### Policy
A governance, compliance, security, or organizational policy.

### Metric
A measurable business or operational indicator.

### Team
An organizational owner or responsible group.

### Test
A validation mechanism associated with an enterprise entity or behavior.

### Deployment
A record of a software or configuration deployment.

### Incident
A historical failure, degradation, or unexpected event.

### Document
A knowledge artifact containing enterprise information.

---

## 3. Change Types

ECCT must support at least the following change categories:

- API change
- Database/schema change
- Data change
- Business-rule change
- ML-model change
- Process change
- Policy change
- Configuration change
- Service change
- Infrastructure change

---

## 4. Relationship Model

Core relationships include:

- System HAS_SERVICE Service
- Service EXPOSES_API API
- Service USES_DATABASE Database
- Database CONTAINS_DATA_ASSET DataAsset
- DataAsset FEEDS_PIPELINE DataPipeline
- DataPipeline PRODUCES_DATA_ASSET DataAsset
- DataAsset FEEDS_MODEL MLModel
- MLModel USED_BY Service
- BusinessProcess USES_SERVICE Service
- BusinessProcess USES_RULE BusinessRule
- BusinessRule AFFECTS_METRIC Metric
- Service OWNED_BY Team
- DataAsset OWNED_BY Team
- API TESTED_BY Test
- Service TESTED_BY Test
- Entity DOCUMENTED_BY Document
- Entity AFFECTED_BY Incident
- Service DEPLOYED_BY Deployment
- Change TARGETS Entity

---

## 5. Consequence Categories

ECCT evaluates consequences across these domains.

### Technical
Examples:
- API incompatibility
- Service failure
- Broken dependency
- Schema mismatch
- Integration failure

### Data
Examples:
- Data-quality degradation
- Distribution changes
- Missing values
- Invalid values
- Pipeline failures
- Data-contract violations

### Semantic
Examples:
- Business-definition mismatch
- Meaning changes
- Inconsistent interpretation
- Metric-definition conflicts

### Business
Examples:
- KPI impact
- Revenue impact
- Conversion impact
- Customer-segment changes
- Business-rule violations

### Operational
Examples:
- SLA degradation
- Processing-time increase
- Support burden
- Deployment risk
- Pipeline delays

### Model / AI
Examples:
- Feature-distribution shift
- Prediction-distribution shift
- Model-performance degradation
- Concept drift
- Calibration changes

### Compliance / Governance
Examples:
- Policy violations
- Control failures
- Audit issues
- Governance requirements

---

## 6. Evidence Classification

Every important ECCT conclusion should use one of these evidence labels:

- FACT — directly supported by enterprise data or evidence.
- INFERENCE — logically derived from known facts.
- PREDICTION — model-based or probabilistic forecast.
- ASSUMPTION — explicitly assumed because evidence is incomplete.
- UNKNOWN — insufficient evidence to determine the consequence.

ECCT must never present UNKNOWN information as fact.

---

## 7. Change Contract

A proposed change should be represented by a Change Contract containing:

- change_id
- change_type
- title
- description
- target_entity
- current_state
- proposed_state
- affected_domain
- requester
- business_reason
- expected_effect
- constraints
- timestamp
- uncertainty

---

## 8. Consequence Assessment

A Consequence Assessment should contain:

- change summary
- affected entities
- technical consequences
- data consequences
- semantic consequences
- business consequences
- operational consequences
- model/AI consequences
- compliance/governance consequences
- historical evidence
- risk scores
- confidence
- unknowns
- supporting evidence
- recommended verification tests
- approval requirements
- audit information

---

## 9. Risk Model

The initial conceptual risk model is:

Risk = Probability × Impact

Later versions may incorporate:

- technical criticality
- data criticality
- business criticality
- blast radius
- historical incidents
- dependency depth
- uncertainty
- consequence severity
- model confidence

Risk calculations should be deterministic and explainable wherever possible.

---

## 10. AI Responsibility Boundaries

### Deterministic Python / SQL

Use for:

- calculations
- filtering
- entity matching
- relationship traversal
- validation
- aggregation
- threshold checks
- risk feature calculation

### Machine Learning

Use for:

- risk prediction
- classification
- anomaly detection
- probability estimation

### LLM

Use for:

- natural-language change interpretation
- semantic reasoning
- document understanding
- ambiguity detection
- evidence synthesis
- explanation generation

### RAG

Use for:

- retrieving enterprise knowledge
- finding supporting documentation
- retrieving historical incidents
- grounding conclusions in evidence

### Agents

Use only when multi-step investigation requires:

- tool selection
- state
- iteration
- specialized reasoning
- recovery from intermediate failures

Agents must operate within explicit tool and execution boundaries.

---

## 11. ECCT Core Principle

ECCT should answer:

> Before we implement this change, what consequences could it create across the enterprise, how confident are we, what evidence supports those conclusions, and what should we verify before approval?

The system must distinguish clearly between:

1. What is known
2. What is inferred
3. What is predicted
4. What is assumed
5. What is unknown