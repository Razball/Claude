# Client Module — [Client Name]
## Industry-Specific Context Layer

This file is appended to the Protocol Base and served to the client's Claude instance via the MCP server. Every field must be filled during the Sprint. Empty fields produce generic output, which kills perceived value.

---

## Layer 0 — Business Snapshot

- **Company name:**
- **Website:**
- **Industry / sub-industry:**
- **Revenue band:** (e.g., $1M–$3M)
- **Team size:** (total / full-time / contractors)
- **Owner name + role:**
- **Owner's top 3 time sinks (in their own words):**
  1.
  2.
  3.
- **Owner's stated goal for the next 90 days:**

---

## Layer 1 — Customers & Offer

- **Primary customer (who buys):**
- **End user (if different):**
- **Core offer (what they sell, in one sentence):**
- **Price point / AOV:**
- **Margin profile:** (high / medium / low + rough %)
- **Main objections in the sales process:**
- **Current blended CAC:**
- **Target CAC:**

---

## Layer 2 — Operations

- **Lead source breakdown:** (e.g., Meta 60%, Google 25%, referral 15%)
- **Sales motion:** (self-serve / inside sales / outside / hybrid)
- **Tools in use:** (CRM, ad platforms, email, SMS, support, billing)
- **Approved tool for each job:** (see Protocol P7 — tool resolution)
- **Team roles & responsibilities:**
- **What the owner personally touches every day:**
- **What the owner has tried to delegate and taken back:**

---

## Layer 3 — Communication Voice

- **Brand voice (3 adjectives):**
- **Banned phrases:**
- **Required phrases:**
- **Preferred CTA style:**
- **Email sign-off:**
- **Sample customer-facing copy (paste 3 real examples):**

---

## Layer 4 — Metrics That Matter

- **North star metric:**
- **Weekly KPIs:** (3–5 max)
- **Current baseline for each:**
- **Target for each (90 days):**
- **Who reports these today?**
- **Where does the data live?**

---

## Layer 5 — Known Patterns

- Recurring tasks the owner does (any cadence):
- Recurring customer questions:
- Known seasonal patterns:

---

## Layer 6 — Proactive Triggers

Conditions that should surface a recommendation automatically. Format: `when [observation], suggest [action]`.

- when
- when
- when

---

## Layer 7 — Escalation & Boundaries

Client-specific overrides to Protocol P8.

- Auto-send allowed for:
- Never send without owner approval:
- Spend limits:

---

## Layer 8 — Active Agents

List of automations deployed for this client. Cross-references `automation-library/deployed/[client]/`.

- **Agent 1 —** [name] — [status]
- **Agent 2 —** [name] — [status]

---

## Layer 9 — Known Facts Index

Pointer to `vault/client-context/known/` entries. Do not duplicate facts here.

---

## Layer 10 — Unknowns & Priority Questions

Pointer to `vault/client-context/unknown/` entries. Top 5 unresolved questions that would meaningfully change the system's behavior if answered.

---

## Version

- v0.1 — [date] — initial draft from Sprint session [N]
