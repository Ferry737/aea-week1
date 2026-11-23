from aea.config import RunConfig
from aea.runner import run_simulation


def test_identical_config_reproduces_events_ledger_and_digest():
    config = RunConfig(seed=881726454633, agents=5, ticks=100)
    first = run_simulation(config)
    second = run_simulation(config)
    assert [event.to_dict() for event in first.events] == [event.to_dict() for event in second.events]
    assert first.ledger.entries == second.ledger.entries
    assert first.digest == second.digest


def test_different_seed_changes_digest():
    base = RunConfig(seed=881726454633, agents=5, ticks=100)
    first = run_simulation(base)
    second = run_simulation(base.model_copy(update={"seed": base.seed + 1}))
    assert first.digest != second.digest
