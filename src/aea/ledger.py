"""Smallest correct in-memory double-entry ledger.

Amounts are signed integer minor units: positive = debit, negative = credit.
Entries are append-only; balances are always derived, never stored.
"""

from dataclasses import dataclass

ASSET_PREFIXES = ("treasury", "agent:")


class LedgerError(Exception):
    """Base class for ledger invariant violations."""


class UnbalancedTransactionError(LedgerError):
    """Raised when the signed sum of a transaction's entries is not zero."""


class InsufficientFundsError(LedgerError):
    """Raised when a transaction would drive an asset account negative."""


def is_asset(account: str) -> bool:
    return account == "treasury" or account.startswith("agent:")


@dataclass(frozen=True)
class Entry:
    account: str
    amount_minor: int

    def __post_init__(self) -> None:
        if not isinstance(self.amount_minor, int) or isinstance(self.amount_minor, bool):
            raise TypeError("amount_minor must be an integer")


@dataclass(frozen=True)
class Transaction:
    tx_id: str
    tick: int
    seq: int
    entries: tuple[Entry, ...]
    memo: str


@dataclass(frozen=True)
class Ledger:
    entries: tuple[Entry, ...] = ()

    @classmethod
    def empty(cls) -> "Ledger":
        return cls(entries=())

    def balance(self, account: str) -> int:
        return sum(e.amount_minor for e in self.entries if e.account == account)

    def asset_supply(self) -> int:
        return sum(e.amount_minor for e in self.entries if is_asset(e.account))

    def post(self, transaction: Transaction) -> "Ledger":
        if sum(e.amount_minor for e in transaction.entries) != 0:
            raise UnbalancedTransactionError(transaction.tx_id)

        proposed = self.entries + transaction.entries
        balances: dict[str, int] = {}
        for entry in proposed:
            balances[entry.account] = balances.get(entry.account, 0) + entry.amount_minor
        for account, balance in balances.items():
            if is_asset(account) and balance < 0:
                raise InsufficientFundsError(account)
        return Ledger(entries=proposed)
