# Automation Library

Pre-built, client-agnostic n8n workflow templates. When the AMP system recognizes a pattern in a client conversation, it matches to a template here and offers to activate.

## Structure

```
automation-library/
├── templates/               # abstracted, client-agnostic
│   ├── 01-lead-response-sequencing/
│   ├── 02-commission-attribution/
│   ├── 03-cs-email-routing/
│   ├── 04-weekly-performance-report/
│   └── 05-appointment-followup/
└── deployed/                # live per-client instances
    └── [client]/[agent-name]/
```

## Template rule

Every template has:
- `README.md` — plain-English description, trigger, input, output, failure modes
- `workflow.json` — n8n export (empty placeholder until extracted)
- `config-schema.md` — what Client Module fields this template needs
- `activation-script.md` — Jackson's step-by-step to deploy per client (<20 min target)

## Priority list (from B3)

1. Lead response sequencing — form fill → instant contact → follow-up
2. Commission/sales attribution — rep tracking + weekly report
3. Customer service email routing and drafting — returns, support tickets
4. Weekly performance reporting — ad + revenue pull
5. Appointment follow-up sequencing

## Source of truth

Templates 2 and 3 are extracted from EzLift Agents 1 and 2 (return handler + commission). The EzLift version is the template. Abstract in place — do not wait for a second client to notice the pattern.
