# EzLift — Agent 1 — Return Email Handler

## Status
Production-ready, awaiting deployment.

## Role
First deployed instance of template `03-cs-email-routing/`, scoped to return requests only.

## Trigger
Inbound email containing return/refund intent.

## Input
- Email (subject + body)
- Customer order history (GHL)
- Product-specific return policy

## Logic
1. Classify as "return request" with confidence score.
2. Pull order details.
3. Draft empathetic reply with:
   - Acknowledgment of the concern
   - Return policy specifics
   - Clear next step (return label, exchange offer, escalation)
4. Add GHL note.
5. Route to owner review queue (no auto-send in v1).

## Output
- Drafted reply in Gmail/GHL
- GHL contact note with classification + action taken

## Escalation
- Emotional/complaint tone → flag for owner
- Order > $X → always owner review
- Multi-unit order → always owner review

## Next step
Deploy to live inbox. Run in shadow mode for 7 days (draft only, owner sends). Then evaluate auto-send whitelist.

## Abstraction notes
- Hardcoded references to EzLift products and policies → move to Client Module Layer 1/7
- Return-specific tone → generalize to "intent-specific tone map"
