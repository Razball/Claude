# Client Module — EzLift
## Industry-Specific Context Layer (Proof of Concept)

EzLift is AMP's first client and product validation instance. Everything here is also a template candidate. Mark fields `[TEMPLATE]` if they generalize, `[CLIENT]` if EzLift-specific.

---

## Layer 0 — Business Snapshot

- **Company name:** EzLift
- **Website:** _TBD_
- **Industry / sub-industry:** Mobility / home independence products (DTC + caregiver market)
- **Revenue band:** _fill_
- **Team size:** _fill_
- **Owner:** Jackson — founder / operator
- **Owner's top 3 time sinks:**
  1. Ad creation and iteration
  2. Customer service email triage
  3. Sales attribution and reporting
- **Owner's 90-day goal:** Drive blended CPP below current $269.70 baseline while scaling autonomous operations.

---

## Layer 1 — Customers & Offer

- **Primary customer:** Adult caregiver children (35–65) buying for a parent
- **End user:** Older adult experiencing mobility decline
- **Core offer:** Premium independence-at-home product (lift/mobility aid)
- **Price point:** _fill_
- **Margin profile:** _fill_
- **Main objections:** Price, "will it actually work for my parent," installation concern
- **Current blended CAC (CPP):** $269.70 (baseline — Apr 2026)
- **Target CPP:** _fill_

---

## Layer 2 — Operations

- **Lead source breakdown:** Meta primary — _fill exact %_
- **Sales motion:** DTC + phone-assist for hesitant buyers
- **Tools in use:** GoHighLevel (CRM, SMS, email), Meta Ads, Google Drive, n8n, Gemini (ad creator)
- **Tool-for-job map:**
  - CRM, contact records, pipeline → GHL
  - Outbound/inbound SMS & email → GHL
  - Ad generation → Gemini + n8n pipeline (see `automation-library/deployed/ezlift/ad-creator`)
  - Automation orchestration → n8n
  - Reporting → GHL + weekly roll-up in vault
- **Team roles:** Jackson (operator), _others TBD_
- **Owner touches daily:** Ad approvals, CS edge cases, margin review
- **Tried to delegate, took back:** _fill_

---

## Layer 3 — Communication Voice

- **Brand voice:** Warm, confident, caregiver-empathetic
- **Banned phrases:** "elderly" (use "older adult" or name the relationship), "handicapped"
- **Required phrases:** _fill from 3 best-performing ads_
- **Preferred CTA style:** Low-pressure, reassurance-forward
- **Email sign-off:** _fill_
- **Sample copy:** _paste 3 top-performing ad captions_

---

## Layer 4 — Metrics That Matter

- **North star:** Autonomous revenue (revenue produced without Jackson personally intervening that week)
- **Weekly KPIs:**
  1. Blended CPP
  2. Autonomous task count
  3. Proactive recommendation action rate
  4. Return/refund rate
  5. Commission attribution accuracy
- **Baselines:** CPP $269.70; others pending week-1 capture
- **Reported by:** System (auto-generated weekly scorecard)
- **Data lives in:** GHL + vault `/metrics/`

---

## Layer 5 — Known Patterns

- Daily ad generation — 30 creatives/day via automated pipeline
- Return-request emails arrive in a predictable format — Agent 1 handles first-draft reply
- Commission attribution at week close — Agent 2 handles

---

## Layer 6 — Proactive Triggers

- when CPP trends up 15% week-over-week, surface a creative-fatigue diagnostic
- when return-request volume spikes, surface root-cause clustering
- when a rep's close rate drops below team median 2 weeks running, flag for coaching

---

## Layer 7 — Escalation & Boundaries

- Auto-send allowed: Agent 1 CS drafts after Jackson's one-time approval of template
- Never without approval: paid spend changes, refund approvals >$X, vendor commitments
- Spend limits: _fill_

---

## Layer 8 — Active Agents

- **Agent 1 — Return Email Handler** — status: production-ready, awaiting deployment. See `automation-library/deployed/ezlift/agent-1-return-handler/`.
- **Agent 2 — Commission Attribution** — status: built in GHL, pending go-live. See `automation-library/deployed/ezlift/agent-2-commission/`.
- **Ad Creator Pipeline** — status: live. See `automation-library/deployed/ezlift/ad-creator/`.

---

## Layer 9 — Known Facts Index

See `vault/client-context/known/ezlift/`.

---

## Layer 10 — Unknowns

See `vault/client-context/unknown/ezlift/priority-questions.md`.

---

## Version

- v0.1 — April 2026 — initial draft extracted from existing EzLift operations
