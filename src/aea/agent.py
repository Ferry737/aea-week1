"""Five minimal rule-based agents: observe -> decide -> act.

No LLM, no learned policy, no memory retrieval. Decisions are plain dictionaries and are
therefore serializable into the event payload verbatim.
"""

from dataclasses import dataclass
from typing import Any

from aea.config import RunConfig
from aea.rng import DeterministicRNG

SCALE = 1_000_000


@dataclass(frozen=True)
class Agent:
    agent_id: str
    goal_target_minor: int

    def observe(self, balance_minor: int, tick: int) -> dict[str, Any]:
        return {"balance_minor": balance_minor, "tick": tick}

    def decide(
        self,
        observation: dict[str, Any],
        rng: DeterministicRNG,
        config: RunConfig,
    ) -> dict[str, Any]:
        draw_scaled = int(rng.random() * SCALE)
        balance = observation["balance_minor"]
        if balance < config.reserve_minor:
            action = "WORK"
        elif draw_scaled < int(config.consume_probability * SCALE):
            action = "CONSUME"
        else:
            action = "WORK"
        return {
            "action": action,
            "draw_scaled": draw_scaled,
            "goal": {
                "type": "savings",
                "target_minor": self.goal_target_minor,
                "progress_minor": min(balance, self.goal_target_minor),
            },
        }
