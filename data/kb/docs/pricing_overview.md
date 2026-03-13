---
  doc_id: KB-001
  title: Pricing & Packaging Overview
  owner_team: Sales Ops
  last_updated: 2026-03-05
  effective_date: 2026-03-10
  policy_type: guidance
  source_of_truth: true
  applies_to:
    - Sales
    - Sales Engineering
    - RevOps
  region_scope:
    - US
    - EMEA
    - APAC
---

# Pricing & Packaging Overview

> ⚠️ **Synthetic dataset notice:** This document is **synthetically generated for a portfolio project**. It does not describe any real company, customer, pricing, or policy.

---

## Quick summary

Explains how Northstar Signal is packaged (Starter/Growth/Enterprise), what’s included, and how to position value during discovery. For exceptions (grandfathered definitions), see **Legacy Customer Exceptions** (KB-021).

## Definitions

- **Seat**: A named user who can access the web app and receive notifications.
- **Signal Event**: A normalized activity record created from integrated systems.
- **Workspace**: Tenant boundary containing users, integrations, and settings.
- **Add-on**: Optional feature bundle priced separately from base plan.

## Policy / Guidance

### Standard plans
We sell three plans: **Starter**, **Growth**, **Enterprise**.

**Starter**
- Best for teams up to ~25 seats
- Standard integrations, basic governance

**Growth**
- Adds SSO/SCIM, advanced workflows, higher API quota
- Best for multi-team rollouts

**Enterprise**
- Adds audit logs, custom roles, data residency options (where available)
- Includes higher support commitments (see **Support Tiers** (KB-009))

### Included usage & overages
Each plan includes a monthly allowance of Signal Events. If usage exceeds allowance, overages apply.
- Overage pricing and fair use rules: **Usage Overage Fees & Fair Use** (KB-005)

### Add-ons (common)
- Advanced Analytics
- Conversation Intelligence
- Data Sync Pro
- Sandbox Workspace

### What we do NOT sell
- No on-prem deployments
- No unlimited API by default (see **API Limits** (KB-015))
- No guarantees on model output correctness; service guarantees are limited to SLA

## Common scenarios & examples

**Example — Pilot packaging:**
- 15 seats, Salesforce + Gmail
- Starter + optional Advanced Analytics

**Example — Security-driven upsell:**
- Customer requires EU hosting and audit logs
- Enterprise + Data Residency controls

**Example — API-heavy use case:**
- Customer building internal tooling
- Growth/Enterprise with negotiated API quota addendum

## Exceptions & edge cases

**This guidance does NOT apply to:**
- Legacy accounts with grandfathered usage definitions (see **Legacy Customer Exceptions** (KB-021))

**Edge cases:**
- Multi-year prepay may unlock additional discount band (see **Discounting & Approval Policy** (KB-003)).
- Regional pricing variations must be documented in the order form and approved by Finance.

## Related docs

- **plan_comparison.md** (KB-002)
- **enterprise_discounts.md** (KB-003)
- **overage_fees.md** (KB-005)

## Appendix: FAQ

- **How do I handle a customer citing an outdated doc?**  
  Confirm the **doc_id** and **last_updated** date in the YAML header. Share the latest doc and summarize what changed.

- **Where do I record an exception?**  
  Record exceptions in CRM under the account and attach the approval. Include doc IDs (e.g., KB-001) and an expiry date.

- **What if two docs conflict?**  
  Follow the doc with the most recent **last_updated** date. If still ambiguous, escalate to the owner team listed in YAML.

## Appendix: Change log

- 2026-03-05: Content refresh, additional examples, clearer exception language.
- 2026-03-10: Effective date for the current version.

## Key fields

- **Region applicability:** US, EMEA, APAC
- **Escalation:** Sales Ops → RevOps/Legal/Security as needed
- **Citation guidance:** Cite **doc_id** + section header (e.g., `KB-001 — Exceptions & edge cases`).

