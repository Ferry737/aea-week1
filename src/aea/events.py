"""Canonical serialization and independently verifiable event hash chain."""

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

GENESIS_HASH = "0" * 64


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_hash(value: Mapping[str, Any]) -> str:
    """Hash the canonical form of an event, excluding the stored hash field."""
    payload = {key: item for key, item in value.items() if key != "hash"}
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SimEvent:
    event_id: str
    run_id: str
    tick: int
    seq: int
    actor_id: str | None
    type: str
    payload: dict[str, Any]
    prev_hash: str
    hash: str = field(init=False, default="")

    def __post_init__(self) -> None:
        object.__setattr__(self, "hash", compute_hash(self.to_dict()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "run_id": self.run_id,
            "tick": self.tick,
            "seq": self.seq,
            "actor_id": self.actor_id,
            "type": self.type,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "hash": self.hash,
        }


def verify_chain(events: Sequence[SimEvent | dict[str, Any]]) -> bool:
    previous = GENESIS_HASH
    for item in events:
        record = item.to_dict() if isinstance(item, SimEvent) else dict(item)
        if record.get("prev_hash") != previous:
            return False
        if record.get("hash") != compute_hash(record):
            return False
        previous = record.get("hash")
    return True
