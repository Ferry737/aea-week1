import pytest

from aea.ledger import (
    Entry,
    InsufficientFundsError,
    Ledger,
    Transaction,
    UnbalancedTransactionError,
)


def mint(amount: int, seq: int = 0) -> Transaction:
    return Transaction(
        tx_id=f"tx-{seq:012d}",
        tick=0,
        seq=seq,
        entries=(Entry("treasury", amount), Entry("faucet", -amount)),
        memo="mint",
    )


def pay(account: str, amount: int, seq: int = 1) -> Transaction:
    return Transaction(
        tx_id=f"tx-{seq:012d}",
        tick=1,
        seq=seq,
        entries=(Entry(account, -amount), Entry("agent:0", amount)),
        memo="pay",
    )


def test_transaction_balances_and_supply_invariant():
    ledger = Ledger.empty().post(mint(1000))
    assert sum(entry.amount_minor for entry in ledger.entries) == 0
    assert ledger.balance("treasury") == 1000
    assert ledger.balance("faucet") == -1000
    assert ledger.asset_supply() + ledger.balance("sink") == 1000


def test_balances_are_derived_and_ledger_is_immutable():
    original = Ledger.empty().post(mint(1000))
    updated = original.post(pay("treasury", 100))
    assert original.balance("treasury") == 1000
    assert updated.balance("treasury") == 900
    assert updated.balance("agent:0") == 100
    assert updated.asset_supply() + updated.balance("sink") == 1000


def test_insufficient_funds_are_rejected():
    ledger = Ledger.empty().post(mint(100))
    with pytest.raises(InsufficientFundsError):
        ledger.post(pay("treasury", 500))


def test_no_negative_wallet_balance():
    ledger = Ledger.empty().post(mint(100)).post(pay("treasury", 100))
    overdraw = Transaction(
        tx_id="tx-overdraw",
        tick=2,
        seq=2,
        entries=(Entry("agent:0", -101), Entry("sink", 101)),
        memo="overdraw",
    )
    with pytest.raises(InsufficientFundsError):
        ledger.post(overdraw)


def test_unbalanced_transaction_is_rejected():
    bad = Transaction(
        tx_id="tx-bad",
        tick=0,
        seq=0,
        entries=(Entry("treasury", 10), Entry("faucet", -9)),
        memo="bad",
    )
    with pytest.raises(UnbalancedTransactionError):
        Ledger.empty().post(bad)
