# 02 — Commission / Sales Attribution

## What it does
Attributes closed revenue to the correct sales rep and produces a weekly commission-ready report.

## Trigger
Weekly schedule (end of business day, last day of pay period) + on-demand.

## Input
- Closed-won opportunities in CRM for the period
- Rep assignment field (from CRM)
- Commission rate(s) from Client Module Layer 2

## Logic
1. Pull closed-won deals from CRM for the defined period.
2. Group by rep.
3. Apply rep-specific commission rate (from Client Module).
4. Flag exceptions: missing rep assignment, overrides, split deals.
5. Render report with totals + drill-down.
6. Post to owner-approved destination (email, Drive, dashboard).

## Output
- Weekly commission report (CSV + human-readable)
- Exception list for owner review

## Escalation
- Stop if any deal has no rep assignment. Surface it for owner assignment before running.
- Stop if a rep's attributed total changes by >25% vs. prior period without a matching deal-count change.

## Failure modes
- CRM rep field missing → report can't run; surface immediately
- Duplicate deal IDs → dedupe and warn

## Source
Extracted from EzLift Agent 2. See `deployed/ezlift/agent-2-commission/`.
