# 03 — Customer Service Email Routing & Drafting

## What it does
Reads inbound customer service emails, classifies by intent, and drafts a reply for owner approval (or auto-sends for whitelisted intents).

## Trigger
Inbound email to support address (via IMAP / webhook / inbox integration).

## Input
- Email subject + body
- Sender history (from CRM)
- Order / account context if available
- Client Module: brand voice, banned phrases, required phrases, auto-send whitelist

## Logic
1. Classify intent (return, refund, product question, shipping, complaint, other).
2. Look up customer context.
3. Draft reply in brand voice with relevant facts.
4. If intent is on the auto-send whitelist and confidence > threshold → send.
5. Else → draft in inbox / owner review queue.
6. Log action in CRM contact record.

## Output
- Sent or drafted reply
- CRM note
- Weekly roll-up: intent distribution, auto-send %, time saved estimate

## Escalation
- Refund > owner-defined threshold → always draft, never auto-send
- Emotional / negative sentiment → always draft, flag for review
- Unknown customer → always draft

## Failure modes
- Misclassification → fallback to "other" and always draft
- Multi-intent email → handle highest-urgency intent, flag the rest

## Source
Extracted from EzLift Agent 1 (return handler). Generalized to handle additional intents.
