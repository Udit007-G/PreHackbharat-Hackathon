import json
from dataclasses import dataclass
from pathlib import Path

from config import (
    HINDSIGHT_API_KEY,
    HINDSIGHT_BANK_ID,
    HINDSIGHT_BASE_URL,
    LOCAL_MEMORY_PATH,
)


@dataclass(frozen=True)
class Memory:
    text: str


class LocalMemoryClient:
    def __init__(self, path: str = LOCAL_MEMORY_PATH):
        self.path = Path(path)
        self.memories = self._load()

    def _load(self) -> list[Memory]:
        if not self.path.exists():
            return []

        raw_memories = json.loads(self.path.read_text(encoding="utf-8"))
        return [Memory(text=item["text"]) for item in raw_memories]

    def recall(self, query: str) -> list[Memory]:
        query_terms = {term for term in query.lower().split() if len(term) > 3}

        def score(memory: Memory) -> int:
            text = memory.text.lower()
            return sum(1 for term in query_terms if term in text)

        return [
            memory
            for memory in sorted(self.memories, key=score, reverse=True)
            if score(memory) > 0
        ]

    def retain(self, content: str) -> None:
        self.memories.append(Memory(text=content))
        payload = [{"text": memory.text} for memory in self.memories]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def close(self) -> None:
        return None


class HindsightMemoryClient:
    def __init__(self):
        from hindsight_client import Hindsight

        self.client = Hindsight(
            base_url=HINDSIGHT_BASE_URL,
            api_key=HINDSIGHT_API_KEY,
        )

    def recall(self, query: str) -> list[Memory]:
        results = self.client.recall(
            bank_id=HINDSIGHT_BANK_ID,
            query=query,
        )
        return [Memory(text=item.text) for item in results.results]

    def retain(self, content: str) -> None:
        self.client.retain(
            bank_id=HINDSIGHT_BANK_ID,
            content=content,
        )

    def close(self) -> None:
        self.client.close()


def create_memory_client(use_hindsight: bool = False):
    if use_hindsight:
        if not HINDSIGHT_API_KEY:
            raise RuntimeError("HINDSIGHT_API_KEY is required when --use-hindsight is set.")
        try:
            return HindsightMemoryClient()
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "hindsight-client is not installed. Run: pip install -r requirements.txt"
            ) from exc

    return LocalMemoryClient()
