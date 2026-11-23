# AEA — Week 1

Simulation-first economic agent laboratory. **Week 1 only**: a deterministic core with an
auditable event chain and an in-memory double-entry ledger.

## Scope this week

- Discrete-event simulation; 1 tick = 1 simulated minute.
- Priority queue ordered by exactly `(sim_tick, seq)`; `seq` is monotonic.
- One writer per run, seed-driven, no wall clock, no network, no LLM.
- Five rule-based agents: observe -> decide -> act. Decisions are structured and serializable.
- Append-only, hash-chained events; in-memory append-only double-entry ledger.

## Gates

1. Same seed -> same event sequence, same ledger, same final digest.
2. Every transaction balances; `sum(entries) == 0`; money supply invariant holds.
3. No negative wallet balance; insufficient funds rejected.
4. Every event hash verifies against `prev_hash` and its canonical payload.

## Run

```bash
python -m aea.runner --seed 881726454633 --agents 5 --ticks 100 --out run.jsonl
```

## Tests / lint

```bash
pytest -q
ruff check .
```

## Explicit non-goals

See `docs/decisions/0001-scope.md`. Nothing in that list is implemented here.
