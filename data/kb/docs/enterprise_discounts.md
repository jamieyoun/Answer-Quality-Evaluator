---
    doc_id: KB-003
    title: Discounting & Approval Policy
    owner_team: Sales Ops
    last_updated: 2026-03-08
    effective_date: 2026-03-15
    policy_type: binding
    source_of_truth: true
    applies_to:
      - Sales
      - RevOps
      - Finance
    region_scope:
      - US
      - EMEA
    supersedes: KB-003-OLD
---

# Discounting & Approval Policy

> ⚠️ **Synthetic dataset notice:** This document is **synthetically generated for a portfolio project**. It does not describe any real company, customer, pricing, or policy.

---

## Quick summary

Defines the **discount bands**, approval workflow, and documentation requirements for non-standard pricing. Use this alongside **Billing, Invoicing & Payment Terms** (KB-004) when negotiating payment schedules.

## Definitions

- **List price**: Published price before any discounting or credits.
- **Effective discount**: Total discount including term, prepay, and promotional credits.
- **Approval chain**: Required approvals based on effective discount and term.
- **Strategic deal**: A deal designated by CRO that may use non-standard terms with documented rationale.

## Policy / Guidance

### Discount bands (standard)
- **0–10%**: AE may approve; must be recorded in CRM with rationale.
- **10–20%**: Sales Manager approval required. (Ref: Approval Matrix, §2.1)
- **20–30%**: VP Sales approval + Finance review required. (Ref: Approval Matrix, §2.2)
- **>30%**: CRO approval required; typically limited to multi-year strategic deals. (Ref: Approval Matrix, §2.3)

### Term & prepay modifiers
- **Multi-year**: Additional discount may be granted if expansion milestones are defined in the order form.
- **Prepay**: May exchange payment risk reduction for discount; must comply with Northstar AI revenue policy.

### Documentation requirements (non-negotiable)
Record the following in CRM and attach approvals:
- Deal rationale (competitive match, expansion, strategic logo)
- Final price, term, seat count, included usage, add-ons
- Any customer commitments we make (avoid roadmap promises)
- Renewal uplift assumptions (see **Renewals Policy** (KB-008))

### Guardrails
- Do **not** promise unlimited usage; define quotas + overage rates (see **Usage Overage Fees** (KB-005)).
- Do **not** discount security/compliance features independently; they are tier-gated.
- Any deviation from standard legal terms must follow **Non-Standard Contracts** (KB-019).

## Common scenarios & examples

**Example — Competitive match:**
- Competitor quote is 12% below list
- Offer 10% discount with a 24-month term and define a renewal uplift range

**Example — Multi-year expansion:**
- Offer 18% discount on 36-month term
- Include expansion milestone: +25 seats by end of Q3

**Example — Prepay trade:**
- Customer agrees to annual prepay
- Offer an additional 3% discount, contingent on standard payment terms

## Exceptions & edge cases

**This policy does NOT apply to:**
- Customers governed by grandfathered discount terms (see **Legacy Customer Exceptions** (KB-021))
- Public sector opportunities that require additional clauses and approvals

**Edge cases:**
- **Channel/reseller deals:** Treat reseller margin as a discount equivalent; Finance review required.
- **Net-new logo swaps:** If discount is granted for a case study/reference, attach the reference plan.

## Related docs

- **pricing_overview.md** (KB-001)
- **billing_invoicing.md** (KB-004)
- **renewals_policy.md** (KB-008)
- **non_standard_contracts.md** (KB-019)

## Appendix: FAQ

- **How do I handle a customer citing an outdated doc?**  
  Confirm the **doc_id** and **last_updated** date in the YAML header. Share the latest doc and summarize what changed.

- **Where do I record an exception?**  
  Record exceptions in CRM under the account and attach the approval. Include doc IDs (e.g., KB-003) and an expiry date.

- **What if two docs conflict?**  
  Follow the doc with the most recent **last_updated** date. If still ambiguous, escalate to the owner team listed in YAML.

## Appendix: Change log

- 2026-03-08: Content refresh, additional examples, clearer exception language.
- 2026-03-15: Effective date for the current version.

## Key fields

- **Region applicability:** US, EMEA
- **Escalation:** Sales Ops → RevOps/Legal/Security as needed
- **Citation guidance:** Cite **doc_id** + section header (e.g., `KB-003 — Exceptions & edge cases`).

