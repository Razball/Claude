"""Subscription gate. Phase 1: config-driven. Later: Stripe webhook state."""


class SubscriptionGate:
    def __init__(self, clients_config: dict):
        self.clients = clients_config

    def is_active(self, client_id: str) -> bool:
        client = self.clients.get(client_id)
        if not client:
            return False
        return client.get("subscription_status") == "active"

    def tier(self, client_id: str) -> str:
        return self.clients.get(client_id, {}).get("tier", "sprint")


SUBSCRIPTION_REQUIRED_PROMPT = """
Your AMP subscription is not active. Managed OS features (proactive automation
discovery, weekly optimization, vault updates) are paused until billing is
current. Basic conversation still works.

Contact Jackson to reactivate.
""".strip()
