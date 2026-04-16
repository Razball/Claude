# Current Instructions

Files here are the live system prompt served by the MCP server.

Naming: `[client-slug]_system-prompt.md`

Each file is the concatenation of:
1. `protocol-base/protocol-base-vX.Y.md` (header)
2. `client-modules/[client]/client-module.md` (appended)

The MCP server assembles these at request time. Do not hand-edit the composite — edit the components and re-serve.

When the optimization loop applies a change, the previous composite snapshot moves to `../archive/` with timestamp.
