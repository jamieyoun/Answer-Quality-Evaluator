---
  doc_id: KB-006
  title: Seat Management, True-Ups, and Billing Impact
  owner_team: Finance
  last_updated: 2026-02-28
  effective_date: 2026-03-01
  policy_type: binding
  source_of_truth: true
  applies_to:
    - Sales
    - CS
    - RevOps
    - Finance
  region_scope:
    - US
    - EMEA
    - APAC
---

# Seat Management, True-Ups, and Billing Impact

> ⚠️ **Synthetic dataset notice:** This document is **synthetically generated for a portfolio project**. It does not describe any real company, customer, pricing, or policy.

---

## Quick summary

Enablement guidance for **Seat Management, True-Ups, and Billing Impact** at Northstar AI. This doc is intended to be used with related policies listed below; when policies conflict, follow the most recent **last_updated** date and escalate to the owner team.

## Definitions

- **Policy**: A rule that must be followed unless an approved exception exists.
- **Guidance**: Recommended practice; deviations should be documented.
- **Exception**: A time-bounded deviation from policy with explicit approval.
- **Source of truth**: The authoritative doc for a policy area; other docs should link here.

## Policy / Guidance

### Scope
Applies to all Northstar Signal customers unless explicitly stated.

### Operating principles
1. Prefer written commitments in order forms/SOWs over informal messages.
2. Optimize for repeatability; frequent exceptions should trigger a process/product change.
3. If security/compliance risk is involved, escalate to Security/Legal.

### Steps (internal)
- Identify account, region, timeline, and requester role
- Gather evidence (CRM notes, tickets, logs, contract excerpts)
- Determine whether request is supported vs requires exception
- If exception: define expiry date + rollback plan; record in CRM (Ref: Exception Logging, §1.4)

### Customer-facing communication template
1) Confirm understanding
2) State policy position + rationale
3) Offer compliant alternatives
4) Define next steps + owners

## Common scenarios & examples

**Example — Standard request:**
- Customer asks a how-to question
- Provide steps + cite the relevant section (e.g., "Policy / Guidance")

**Example — Edge case:**
- Customer requests behavior outside documented limits
- Explain the limit, cite the doc, and propose an alternative (batching, scheduling, add-on quota)

**Example — Contractual commitment risk:**
- If request would change SLA or data handling, route through **Non-Standard Contracts** (KB-019)

## Exceptions & edge cases

**This policy does NOT apply to:**
- Explicitly grandfathered terms documented in **Legacy Customer Exceptions** (KB-021)
- Customer commitments written into a signed order form that override defaults

**Edge cases:**
- Regional constraints may apply (see YAML `region_scope`).
- If a related doc is newer and conflicts with this one, follow the newer doc and flag the conflict.

## Related docs

- **billing_invoicing.md** (KB-004)
- **renewals_policy.md** (KB-008)

## Appendix: FAQ

- **How do I handle a customer citing an outdated doc?**  
  Confirm the **doc_id** and **last_updated** date in the YAML header. Share the latest doc and summarize what changed.

- **Where do I record an exception?**  
  Record exceptions in CRM under the account and attach the approval. Include doc IDs (e.g., KB-006) and an expiry date.

- **What if two docs conflict?**  
  Follow the doc with the most recent **last_updated** date. If still ambiguous, escalate to the owner team listed in YAML.

## Appendix: Change log

- 2026-02-28: Content refresh, additional examples, clearer exception language.
- 2026-03-01: Effective date for the current version.

## Key fields

- **Region applicability:** US, EMEA, APAC
- **Escalation:** Finance → RevOps/Legal/Security as needed
- **Citation guidance:** Cite **doc_id** + section header (e.g., `KB-006 — Exceptions & edge cases`).

