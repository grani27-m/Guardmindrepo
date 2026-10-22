from lba_guardrail.tape import BoundedTape


def test_append_keeps_recent_history_only():
    tape = BoundedTape(tape_length=3)
    for item in ["a", "b", "c", "d"]:
        tape.append(item)

    assert tape.snapshot() == ("b", "c", "d")


def test_snapshot_is_immutable_and_hashable():
    tape = BoundedTape(tape_length=2)
    tape.append("x")
    tape.append("y")

    snapshot = tape.snapshot()
    assert isinstance(snapshot, tuple)
    assert hash(snapshot) == hash(snapshot)
    assert snapshot == ("x", "y")


def test_identical_history_produces_equal_snapshots():
    tape_one = BoundedTape(tape_length=4)
    tape_two = BoundedTape(tape_length=4)

    for value in ["r1", "r2", "r3"]:
        tape_one.append(value)
        tape_two.append(value)

    assert tape_one.snapshot() == tape_two.snapshot()
