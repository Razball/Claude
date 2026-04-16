# Optimization Vault

The data layer the Managed OS subscription is built on. Obsidian-compatible markdown, Git-versioned. One vault per client.

## Structure

```
vault/
├── instructions/
│   ├── current/            # live system prompt served by MCP (protocol-base + client-module)
│   └── archive/            # every previous version, timestamped
├── reflect-logs/           # one file per session, append-only
├── agent-configs/          # spec + status per deployed agent
├── optimization/
│   ├── proposed/           # pending changes from weekly loop
│   └── applied/            # approved changes + diff
├── metrics/                # weekly scorecards
└── client-context/
    ├── known/              # confirmed facts
    └── unknown/            # prioritized gaps
```

## File naming

- Reflect logs: `YYYY-MM-DD_HHMM_topic-slug.md`
- Instruction versions: `YYYY-MM-DD_vX.Y.md`
- Optimization proposals: `YYYY-MM-DD_proposal-slug.md`
- Metrics: `YYYY-MM-DD_weekly-scorecard.md`

## Rules

- Append-only: reflect logs are never edited after write.
- Every applied optimization must include a diff against the previous `instructions/current/`.
- `known/` vs `unknown/` enforces Protocol P9 (memory discipline). Never move to `known/` without confirmation.
