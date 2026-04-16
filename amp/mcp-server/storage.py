"""Storage adapter. Local filesystem for Phase 1; swap to object store later."""

from pathlib import Path
from datetime import datetime


class LocalStorage:
    def __init__(self, root: str):
        self.root = Path(root).resolve()

    def read_text(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8")

    def append_reflect_log(self, client_id: str, payload: str) -> str:
        ts = datetime.utcnow().strftime("%Y-%m-%d_%H%M")
        filename = f"{ts}_{client_id}.md"
        path = self.root / "vault" / "reflect-logs" / filename
        path.write_text(payload, encoding="utf-8")
        return str(path.relative_to(self.root))

    def list_known_facts(self, client_id: str) -> str:
        client_dir = self.root / "vault" / "client-context" / "known" / client_id
        if not client_dir.exists():
            return ""
        chunks = []
        for file in sorted(client_dir.glob("*.md")):
            chunks.append(file.read_text(encoding="utf-8"))
        return "\n\n".join(chunks)

    def append_unknown(self, client_id: str, fact: str) -> str:
        client_dir = self.root / "vault" / "client-context" / "unknown" / client_id
        client_dir.mkdir(parents=True, exist_ok=True)
        path = client_dir / "proposed.md"
        with path.open("a", encoding="utf-8") as f:
            f.write(f"\n- [{datetime.utcnow().isoformat()}] {fact}\n")
        return str(path.relative_to(self.root))
