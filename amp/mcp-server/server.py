"""AMP MCP Server — Phase 1 scaffold.

Serves each client's composite system prompt (Protocol Base + Client Module)
and accepts reflect-log writes. Runs as a FastMCP server.

Boot: python server.py --config config.yaml
"""

from pathlib import Path
import argparse
import yaml

from fastmcp import FastMCP

from storage import LocalStorage
from subscription import SubscriptionGate, SUBSCRIPTION_REQUIRED_PROMPT


def load_config(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def build_server(config: dict) -> FastMCP:
    mcp = FastMCP("amp")
    storage = LocalStorage(config["storage"]["root"])
    gate = SubscriptionGate(config["clients"])
    protocol_base_path = config["protocol_base"]["path"]

    @mcp.tool()
    def get_instructions(client_id: str) -> str:
        """Return the composite system prompt for a client.

        Called once at the start of every Claude conversation. Returns
        Protocol Base + Client Module as a single string. If subscription
        is inactive, returns the subscription-required prompt instead.
        """
        if not gate.is_active(client_id):
            return SUBSCRIPTION_REQUIRED_PROMPT

        client = config["clients"].get(client_id)
        if not client:
            return f"Unknown client_id: {client_id}"

        base = storage.read_text(protocol_base_path)
        module = storage.read_text(client["module_path"])
        return f"{base}\n\n---\n\n{module}"

    @mcp.tool()
    def log_reflect(client_id: str, payload: str) -> dict:
        """Append a reflect log entry for a client session."""
        if not gate.is_active(client_id):
            return {"status": "inactive", "written": None}
        written = storage.append_reflect_log(client_id, payload)
        return {"status": "ok", "written": written}

    @mcp.tool()
    def get_known_facts(client_id: str) -> str:
        """Return confirmed client-context facts."""
        if not gate.is_active(client_id):
            return ""
        return storage.list_known_facts(client_id)

    @mcp.tool()
    def propose_fact(client_id: str, fact: str) -> dict:
        """Append an unconfirmed fact for owner review."""
        if not gate.is_active(client_id):
            return {"status": "inactive", "written": None}
        written = storage.append_unknown(client_id, fact)
        return {"status": "ok", "written": written}

    return mcp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    mcp = build_server(config)
    mcp.run()


if __name__ == "__main__":
    main()
