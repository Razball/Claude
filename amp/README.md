# AMP — Applied Multiplier Partners

Productized AI operating system for small business owners. This directory is the source of truth for the AMP product: protocol, vault, modules, automation library, onboarding, and the MCP server that serves it all.

## Directory map

```
amp/
├── README.md                        # this file
├── builder-instructions.md          # v4.1 system prompt (Section A + B)
├── protocol-base/                   # client-agnostic product layer
│   └── protocol-base-v3.1.md
├── client-modules/                  # one folder per client
│   ├── _template/                   # blank client module scaffold
│   └── ezlift/                      # first client (proof of concept)
├── vault/                           # optimization data layer
│   ├── instructions/{current,archive}
│   ├── reflect-logs/
│   ├── agent-configs/
│   ├── optimization/{proposed,applied}
│   ├── metrics/
│   └── client-context/{known,unknown}
├── automation-library/              # pre-built n8n workflow templates
│   ├── templates/                   # abstracted, client-agnostic
│   └── deployed/                    # live per-client instances
├── onboarding/                      # sprint playbook
└── mcp-server/                      # delivery mechanism (Path 1)
```

## How the pieces fit

1. **Client's Claude Project** holds one instruction: call `get_instructions()` on the AMP MCP server.
2. **MCP server** returns `protocol-base` + the client's `client-module` as a single system prompt.
3. **Client conversation** happens. Reflect logs are captured and written to `vault/reflect-logs/`.
4. **Optimization loop** (weekly n8n job) reads reflect logs, proposes instruction updates in `vault/optimization/proposed/`, applies approved changes to `vault/instructions/current/`, archives previous versions.
5. **Automation library** is matched against conversation patterns. When the system sees a repeated pattern, it offers to activate a template.

## Build sequence (from B6)

| Phase | Status |
|---|---|
| Now — Run second client manually | pending |
| Phase 1 — MCP server live, serving EzLift | pending |
| Phase 2 — Vault deployed, reflect capture wired | designed |
| Phase 3 — Automation library from EzLift Agents 1 and 2 | Agents built, not yet abstracted |
| Phase 4 — Onboarding playbook from second client run | pending |
| Phase 5 — First paying non-EzLift client | pending |
| Phase 6 — API wrapper + branded interface | deferred |

## Rules

- Protocol Base is client-agnostic. If a section needs domain knowledge, it belongs in the Client Module.
- Every EzLift artifact is also a product template. Abstract in-place, not later.
- Nothing ships to this repo that can't be built and deployed by one person in under a week.
