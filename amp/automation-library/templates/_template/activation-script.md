# Activation Script — [Automation Name]

Jackson's step-by-step to deploy this template for a new client. Target total time: under 20 minutes.

## Pre-flight
- [ ] Client Module has required fields (see `config-schema.md`)
- [ ] Secrets stored in client's n8n credential store
- [ ] Trigger source (webhook, inbound, schedule) confirmed

## Steps
1. Import `workflow.json` into client's n8n instance.
2. Map credentials: [list credential nodes].
3. Set environment variables per `config-schema.md`.
4. Run smoke test with synthetic input.
5. Activate trigger.
6. Log in `vault/agent-configs/` with status=live.
7. Update `client-modules/[client]/client-module.md` Layer 8.

## Rollback
How to disable safely if the automation misbehaves.

## Success criterion
What metric moves in the first 7 days if this is working?
