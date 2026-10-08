# Phase 2 — Synthetic Enterprise Dataset

## Purpose

Phase 2 establishes a realistic, internally consistent synthetic enterprise
environment for the Enterprise Change Consequence Twin (ECCT).

The purpose is to create an enterprise world that ECCT can later investigate
when analyzing proposed changes.

The dataset must support:

- dependency analysis
- data lineage analysis
- business-process impact analysis
- ownership lookup
- historical evidence retrieval
- incident analysis
- change-history analysis
- test and deployment analysis
- business-metric impact analysis
- RAG evaluation
- agentic investigation
- consequence ground-truth evaluation

All data in this phase is explicitly synthetic.

No synthetic record should be presented as real-world enterprise evidence.

---

## Synthetic Enterprise

**Name:** Acme Commerce Platform

**Industry:** Digital Commerce

### Core Business Capabilities

- Customer Management
- Order Management
- Eligibility Management
- Payments
- Marketing
- Analytics

---

## Enterprise Backbone

The initial enterprise dependency chain is:

```text
Customer
   │
   ▼
Web / Mobile
   │
   ▼
Customer API
   │
   ▼
Customer Service
   │
   ├──────────────► Eligibility Service
   │                    │
   │                    ▼
   │              Eligibility Rule
   │                    │
   │                    ▼
   │              Customer Database
   │                    │
   │                    ▼
   │              Customer Data Asset
   │                    │
   │                    ▼
   │              Customer Pipeline
   │                    │
   │                    ▼
   │              Segmentation Model
   │                    │
   │                    ▼
   │              Marketing Service
   │
   ▼
Order Service
   │
   ▼
Checkout Process
   │
   ▼
Revenue / Conversion Metrics