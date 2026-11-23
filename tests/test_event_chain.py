from aea.events import SimEvent, canonical_json, compute_hash, verify_chain


def make_event(seq: int, payload: dict, prev_hash: str) -> SimEvent:
    return SimEvent(
        event_id=f"evt-{seq:012d}",
        run_id="run-test",
        tick=seq,
        seq=seq,
        actor_id="agent:0",
        type="AGENT_DECISION",
        payload=payload,
        prev_hash=prev_hash,
    )


def test_event_hash_matches_canonical_payload():
    event = make_event(1, {"action": "WORK", "amount_minor": 100}, "0" * 64)
    assert isinstance(canonical_json(event.to_dict()), str)
    assert event.hash == compute_hash(event.to_dict())
    assert event.hash == compute_hash({"payload": {"amount_minor": 100, "action": "WORK"}, **event.to_dict()})


def test_chain_verifies_and_detects_tampering():
    first = make_event(1, {"action": "WORK"}, "0" * 64)
    second = make_event(2, {"action": "CONSUME"}, first.hash)
    assert verify_chain([first, second]) is True
    tampered = second.to_dict()
    tampered["payload"] = {**tampered["payload"], "injected": True}
    assert compute_hash(tampered) != second.hash
    assert verify_chain([first, tampered]) is False


def test_canonical_serialization_is_key_order_independent():
    assert canonical_json({"b": 2, "a": 1}) == canonical_json({"a": 1, "b": 2})
