# EzLift — Agent 2 — Commission Attribution

## Status
Built in GHL, pending go-live.

## Role
First deployed instance of template `02-commission-attribution/`.

## Trigger
Weekly schedule + on-demand.

## Input
- GHL closed-won opportunities
- Rep assignment on the opportunity
- Commission rates per rep (Client Module Layer 2)

## Logic
1. Pull last-week closed-won from GHL.
2. Group by `assigned_to`.
3. Apply rep commission rate.
4. Flag deals with missing rep or split attribution.
5. Render report.
6. Post to owner (email + Drive).

## Output
- Weekly commission report
- Exception list

## Escalation
- Missing rep on any deal → surface and stop before posting final report
- Week-over-week total change >25% → flag

## Next step
Go-live check: validate rates per rep, run first week in parallel with manual calc, confirm match.

## Abstraction notes
- GHL-specific API calls → generalize to "CRM adapter" (GHL, HubSpot, Pipedrive)
- Commission calc is already generic — safe to extract
