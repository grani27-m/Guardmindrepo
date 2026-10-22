from lba_guardrail.agents.mock_agent import SolvableTaskAgent, ImpossibleTaskAgent
from lba_guardrail.automaton import LBAGuardrail
from lba_guardrail.middleware import run_with_guardrail, SUCCESS, HALTED_BY_LBA, RAN_OUT_OF_STEPS


def test_solvable_agent_returns_success():
    result = run_with_guardrail(SolvableTaskAgent(), LBAGuardrail(tape_length=4), max_steps=10)
    assert result == SUCCESS


def test_impossible_agent_gets_halted():
    result = run_with_guardrail(ImpossibleTaskAgent(), LBAGuardrail(tape_length=4), max_steps=20)
    assert result == HALTED_BY_LBA


def test_no_guardrail_runs_to_cap():
    result = run_with_guardrail(ImpossibleTaskAgent(), guardrail=None, max_steps=20)
    assert result == RAN_OUT_OF_STEPS
