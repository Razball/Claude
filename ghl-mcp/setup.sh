#!/bin/bash
# GoHighLevel MCP Server — one-time local setup script
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Installing Python dependencies..."
pip install -q mcp[cli] httpx python-dotenv pydantic

echo "==> Creating .env file..."
cat > "$SCRIPT_DIR/.env" <<EOF
GHL_API_KEY=pit-5cadac89-b0cf-4987-8d91-3800e8a9d9de
GHL_LOCATION_ID=COt34myIuJYhlau1Nxl5
GHL_BASE_URL=https://services.leadconnectorhq.com
EOF

echo "==> Registering MCP server with Claude Code..."
claude mcp add gohighlevel python3 "$SCRIPT_DIR/server.py"

echo ""
echo "✓ Done! Restart Claude Code and your GHL tools will be available."
