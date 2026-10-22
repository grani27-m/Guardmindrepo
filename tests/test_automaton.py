from lba_guardrail.automaton import LBAGuardrail


def test_no_repeat_never_halts():
    guardrail = LBAGuardrail(tape_length=3)

    for state, observation in [
        ("s0", "a"),
        ("s0", "b"),
        ("s1", "c"),
        ("s1", "d"),
    ]:
        assert guardrail.step(state, observation) is True

    assert guardrail.halted is False


def test_repeat_triggers_halt_at_second_repetition():
    guardrail = LBAGuardrail(tape_length=2)
    sequence = [
        ("s0", "alpha"),
        ("s0", "beta"),
        ("s0", "alpha"),
        ("s0", "beta"),
    ]

    assert guardrail.step(sequence[0][0], sequence[0][1]) is True
    assert guardrail.step(sequence[1][0], sequence[1][1]) is True
    assert guardrail.step(sequence[2][0], sequence[2][1]) is True
    assert guardrail.step(sequence[3][0], sequence[3][1]) is False
    assert guardrail.halted is True


def test_max_theoretical_configurations():
    guardrail = LBAGuardrail(tape_length=3)
    value = guardrail.max_theoretical_configurations(num_states=6, alphabet_size=5)
    assert value == 6 * 3 * (5 ** 3)
    assert value == 2250
