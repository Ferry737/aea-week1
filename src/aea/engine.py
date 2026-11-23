"""Discrete-event engine with a pure reducer and exact (sim_tick, seq) ordering."""

import hashlib
import heapq
from dataclasses import dataclass, replace
from typing import Any

from aea.agent import Agent
from aea.config import RunConfig
from aea.events import GENESIS_HASH, SimEvent, canonical_json
from aea.ledger import Entry, InsufficientFundsError, Ledger, Transaction
from aea.rng import DeterministicRNG, derive_seed


@dataclass(frozen=True)
class PendingEvent:
    tick: int
    seq: int
    type: str
    actor_id: str | None
    payload: dict[str, Any]


@dataclass(frozen=True)
class SimState:
    run_id: str
    ledger: Ledger
    events: tuple[SimEvent, ...]
    rng_states: dict[str, Any]


def make_run_id(config: RunConfig) -> str:
    digest = hashlib.sha256(canonical_json(config.model_dump()).encode("utf-8")).hexdigest()
    return f"run-{digest[:16]}"


def build_schedule(config: RunConfig) -> dict[tuple[int, int], PendingEvent]:
    schedule: dict[tuple[int, int], PendingEvent] = {}
    seq = 0
    schedule[(0, seq)] = PendingEvent(
        tick=0,
        seq=seq,
        type="MINT",
        actor_id=None,
        payload={
            "amount_minor": config.money_supply_minor,
            "currency": config.currency,
        },
    )
    seq += 1
    for tick in range(1, config.ticks + 1):
        for index in range(config.agents):
            schedule[(tick, seq)] = PendingEvent(
                tick=tick,
                seq=seq,
                actor_id=f"agent:{index}",
                type="AGENT_DECISION",
                payload={},
            )
            seq += 1
    return schedule


def _mint(state: SimState, pending: PendingEvent, config: RunConfig) -> tuple[Ledger, dict[str, Any]]:
    amount = pending.payload["amount_minor"]
    transaction = Transaction(
        tx_id=f"tx-{pending.seq:012d}",
        tick=pending.tick,
        seq=pending.seq,
        entries=(Entry("treasury", amount), Entry("faucet", -amount)),
        memo="mint",
    )
    return state.ledger.post(transaction), {
        "amount_minor": amount,
        "currency": config.currency,
        "tx_id": transaction.tx_id,
    }


def _decide(
    state: SimState,
    pending: PendingEvent,
    config: RunConfig,
) -> tuple[Ledger, dict[str, Any], dict[str, Any]]:
    actor = pending.actor_id
    assert actor is not None
    rng = DeterministicRNG(derive_seed(config.seed, actor))
    rng.setstate(state.rng_states[actor])
    agent = Agent(agent_id=actor, goal_target_minor=config.money_supply_minor // config.agents)
    observation = agent.observe(state.ledger.balance(actor), pending.tick)
    decision = agent.decide(observation, rng, config)
    new_rng_state = rng.getstate()

    action = decision["action"]
    executed = "IDLE"
    if action == "WORK":
        amount = config.wage_minor
        entries = (Entry("treasury", -amount), Entry(actor, amount))
        memo = "wage"
    else:
        amount = config.consume_minor
        entries = (Entry(actor, -amount), Entry("sink", amount))
        memo = "consume"
    tx_id = f"tx-{pending.seq:012d}"

    ledger = state.ledger
    try:
        ledger = ledger.post(
            Transaction(
                tx_id=tx_id,
                tick=pending.tick,
                seq=pending.seq,
                entries=entries,
                memo=memo,
            )
        )
        executed = action
    except InsufficientFundsError:
        pass

    payload = {
        "observation": observation,
        "decision": {
            "action": decision["action"],
            "draw_scaled": decision["draw_scaled"],
            "goal": decision["goal"],
        },
        "executed": executed,
        "amount_minor": amount if executed != "IDLE" else 0,
        "tx_id": tx_id if executed != "IDLE" else None,
    }
    return ledger, payload, new_rng_state


def reduce_state(state: SimState, pending: PendingEvent, config: RunConfig) -> SimState:
    """Pure state transition: no clock, no I/O, no hidden randomness."""
    rng_states = state.rng_states
    if pending.type == "MINT":
        ledger, payload = _mint(state, pending, config)
    elif pending.type == "AGENT_DECISION":
        ledger, payload, new_rng_state = _decide(state, pending, config)
        rng_states = {**rng_states, pending.actor_id: new_rng_state}
    else:
        raise ValueError(f"unknown event type: {pending.type}")

    event = SimEvent(
        event_id=f"evt-{pending.seq:012d}",
        run_id=state.run_id,
        tick=pending.tick,
        seq=pending.seq,
        actor_id=pending.actor_id,
        type=pending.type,
        payload=payload,
        prev_hash=state.events[-1].hash if state.events else GENESIS_HASH,
    )
    return replace(state, ledger=ledger, events=state.events + (event,), rng_states=rng_states)


def initial_state(config: RunConfig) -> SimState:
    rng_states = {
        f"agent:{index}": DeterministicRNG(derive_seed(config.seed, f"agent:{index}")).getstate()
        for index in range(config.agents)
    }
    return SimState(
        run_id=make_run_id(config),
        ledger=Ledger.empty(),
        events=(),
        rng_states=rng_states,
    )


def run_state(config: RunConfig) -> SimState:
    schedule = build_schedule(config)
    keys = sorted(schedule)
    heapq.heapify(keys)
    state = initial_state(config)
    for key in keys:
        state = reduce_state(state, schedule[key], config)
    return state
