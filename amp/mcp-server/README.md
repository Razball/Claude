# AMP MCP Server

Serves each client's composite system prompt (Protocol Base + their Client Module) on demand. One instruction in the client's Claude Project tells it to call `get_instructions()` on every new conversation.

## Why MCP (not Claude Projects file upload)

Solves four problems with one mechanism:
1. **IP protection** — Protocol Base never touches the client's side; it lives on the server.
2. **Instruction updates** — change once, every client sees it on next conversation. No file swaps.
3. **Subscription gating** — if `client_id` subscription is inactive, return a soft "subscription required" prompt.
4. **Data capture** — the call is the checkpoint where session metadata can be initialized.

## Endpoints

| Tool | Purpose |
|---|---|
| `get_instructions(client_id)` | Returns Protocol Base + Client Module composite |
| `log_reflect(client_id, payload)` | Writes a reflect log entry to `vault/reflect-logs/` |
| `get_known_facts(client_id)` | Returns confirmed client-context facts |
| `propose_fact(client_id, fact)` | Adds to `unknown/` until confirmed |

## Auth
Each client gets a `client_id` and a short-lived signed token. Tokens check subscription status before serving instructions.

## Storage
- Protocol Base + Client Modules: this Git repo, pulled at boot and on webhook
- Vault writes: Google Drive (or S3 later) — one prefix per client

## Deploy target (Phase 1)
Single Python process. FastMCP framework. Hosted on Fly.io or Railway. TLS. One environment variable for the storage backend path.

## Files
- `server.py` — MCP server skeleton (FastMCP)
- `storage.py` — file/object storage adapter
- `subscription.py` — subscription gate
- `config.example.yaml` — config template
- `requirements.txt` — deps

## Status
Scaffolding only. Not yet connected to Claude.ai MCP. Phase 1 target: working `get_instructions()` returning EzLift's composite, called from Jackson's own Claude project.
