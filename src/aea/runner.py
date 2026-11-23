"""CLI entry point and deterministic run artifact writer."""

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from aea.config import RunConfig
from aea.engine import run_state
from aea.events import canonical_json, verify_chain
from aea.ledger import Ledger, is_asset


@dataclass(frozen=True)
class RunResult:
    config: RunConfig
    ledger: Ledger
    events: tuple[Any, ...]
    digest: str


def run_simulation(config: RunConfig) -> RunResult:
    state = run_state(config)
    if not verify_chain(state.events):
        raise RuntimeError("event hash chain verification failed")
    records = [event.to_dict() for event in state.events]
    digest = hashlib.sha256(
        canonical_json(
            {
                "run_id": state.run_id,
                "events": records,
                "ledger": [asdict(entry) for entry in state.ledger.entries],
            }
        ).encode("utf-8")
    ).hexdigest()
    return RunResult(config=config, ledger=state.ledger, events=state.events, digest=digest)


def write_run_artifact(result: RunResult, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            json.dumps(
                {"type": "RUN_HEADER", "run_id": result.digest[:16], "digest": result.digest},
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        )
        for event in result.events:
            handle.write(json.dumps(event.to_dict(), sort_keys=True, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(prog="aea.runner")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--agents", type=int, default=5)
    parser.add_argument("--ticks", type=int, default=100)
    parser.add_argument("--out", type=Path, default=Path("run.jsonl"))
    args = parser.parse_args()

    config = RunConfig(seed=args.seed, agents=args.agents, ticks=args.ticks)
    result = run_simulation(config)
    write_run_artifact(result, args.out)

    asset_supply = sum(
        entry.amount_minor for entry in result.ledger.entries if is_asset(entry.account)
    )
    print(f"run_id={result.digest[:16]}")
    print(f"seed={config.seed} agents={config.agents} ticks={config.ticks}")
    print(f"events={len(result.events)}")
    print(f"asset_supply_minor={asset_supply}")
    print(f"ledger_entries={len(result.ledger.entries)}")
    print(f"chain_valid={verify_chain(result.events)}")
    print(f"digest={result.digest}")


if __name__ == "__main__":
    main()
