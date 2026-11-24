<div align="center">

# AEA — Week 1

**A simulation-first laboratory for economic agents.**
Week 1 ships the part most agent projects skip: a **deterministic core** with an auditable, hash-chained event log and a double-entry ledger that cannot silently break.

[![CI](https://github.com/Ferry737/aea-week1/actions/workflows/ci.yml/badge.svg)](https://github.com/Ferry737/aea-week1/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](./pyproject.toml)
[![Determinism](https://img.shields.io/badge/Determinism-seed%20%3D%20same%20digest-2ea44f?style=for-the-badge)](#-gates)
[![Browser harness](https://img.shields.io/badge/Browser%20harness-live-00d4aa?style=for-the-badge&logo=githubpages&logoColor=white)](https://ferry737.github.io/aea-week1/)

[**Open the browser harness →**](https://ferry737.github.io/aea-week1/) · [Run it](#-run) · [Scope decision](./docs/decisions/0001-scope.md)

</div>

---

## 🎯 What this is

An **A**gent-**E**conomy **A**rchitecture built in weekly, verifiable slices. Week 1 is deliberately unglamorous and deliberately boring: no LLM, no network, no wall clock. Just a core you can replay byte-for-byte and audit end-to-end.

> **Week 1 only.** Nothing in the [non-goals](./docs/decisions/0001-scope.md) list is implemented here — on purpose.

## 🔒 Invariants (the whole point)

| # | Gate | Meaning |
|---|---|---|
| 1 | **Determinism** | Same seed → same event sequence, same ledger, same final digest. Every run is reproducible. |
| 2 | **Balance** | Every transaction balances: `sum(entries) == 0`. Money supply is invariant. |
| 3 | **No overdraft** | Negative wallet balances are impossible; insufficient funds are rejected. |
| 4 | **Integrity** | Every event hash verifies against `prev_hash` and its canonical payload. Tamper = detect. |

## 🧩 What's inside

- **Discrete-event engine** — 1 tick = 1 simulated minute. Priority queue ordered by exactly `(sim_tick, seq)`; `seq` is monotonic.
- **One writer per run** — seed-driven RNG, no wall clock, no network, no LLM.
- **Five rule-based agents** — `observe → decide → act`. Decisions are structured and serializable.
- **Hash-chained events** — append-only; each event carries the hash of the one before it.
- **In-memory double-entry ledger** — append-only, invariant-checked.

```
src/aea/
├── engine.py     ← event loop, (sim_tick, seq) ordering
├── events.py     ← hash-chained event types + canonical payload
├── ledger.py     ← double-entry ledger, balance + supply invariants
├── agent.py      ← observe → decide → act
├── rng.py        ← seed-driven randomness
├── config.py
└── runner.py     ← CLI entry point
tests/
├── test_determinism.py
├── test_event_chain.py
└── test_ledger.py
```

## ▶ Run

```bash
pip install -e ".[dev]"          # or: pip install -e .
python -m aea.runner --seed 881726454633 --agents 5 --ticks 100 --out run.jsonl
```

`run.jsonl` is the full event chain — replay it, hash it, diff it against another run with the same seed.

## ✅ Tests / lint

```bash
pytest -q
ruff check .
```

CI runs both on every push.

## 🔭 What's next

Weeks 2+ layer on top of this core rather than rewriting it. Scope decisions live in [`docs/decisions/`](./docs/decisions/) as numbered ADRs, so "why is it like this" always has a paper trail.

---

<div align="center">
<sub>Built by <a href="https://github.com/Ferry737">Ferry</a></sub><br>
<sub>Week 1: make it provable. Everything after that is easier.</sub>
</div>
