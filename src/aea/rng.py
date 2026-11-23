"""Explicit per-agent deterministic RNG. No global random state is used."""

import hashlib
import random
from typing import Any


def derive_seed(master_seed: int, agent_id: str) -> int:
    digest = hashlib.sha256(f"{master_seed}:{agent_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


class DeterministicRNG:
    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)

    def getstate(self) -> Any:
        return self._rng.getstate()

    def setstate(self, state: Any) -> None:
        self._rng.setstate(state)

    def random(self) -> float:
        return self._rng.random()
