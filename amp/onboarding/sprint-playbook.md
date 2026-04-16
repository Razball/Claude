# Sprint Playbook (v0.1 — scaffold)

The guided-conversation onboarding flow. Not a form — a live session that produces the Client Module in real time.

## Session 1 — Business Map (90 minutes, live)

**Goal:** 80% of Layers 0–2 populated.

Open:
> "Before I can be useful, I need to know your business the way an operator would. I'm going to ask questions in a specific order. Each answer shapes the next question."

Flow:
1. Layer 0 — Snapshot (15 min)
2. Layer 1 — Customers & offer (25 min)
3. Layer 2 — Operations & tools (30 min)
4. Wrap: confirm top 3 time sinks → these become the first automation targets (15 min)
5. Reflect log: what was decided, what's still unknown.

Output: `client-modules/[client]/client-module.md` draft, `vault/client-context/unknown/priority-questions.md`, reflect log.

## Session 2 — Voice & Proof (60 minutes, live)

**Goal:** Layer 3 + 2 real example outputs.

1. Paste 3 best-performing pieces of customer copy.
2. Define banned/required phrases.
3. Run live prompt elevation demo using their own question.

Output: Layer 3 complete, 2 sample outputs that pass owner smell-test.

## Session 3 — Automation Priority (60 minutes, async-friendly)

**Goal:** Match their top 3 time sinks to 3 templates from `automation-library/templates/`.

For each: confirm fit, identify gaps, estimate deploy time.

Output: 3 scoped agents on the build queue.

## Session 4 — Go-Live (variable, week 2–4)

**Goal:** First agent live. One automation running in production.

---

## What "done" looks like

- Client Module Layers 0–4, 7, 8 populated
- 1 agent deployed and running
- Vault initialized with reflect logs, metrics baseline
- MCP server serving their instructions
- Owner has received at least one proactive recommendation in conversation

## Time budget
- Jackson's time in session: under 4 hours total across Sprint
- Jackson's time building: under 10 hours across Sprint
- Total Sprint duration: 2–4 weeks
