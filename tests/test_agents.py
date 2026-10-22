import lba_guardrail.agents.llm_agent as llm_agent
from lba_guardrail.agents.mock_agent import SolvableTaskAgent, ImpossibleTaskAgent


def test_solvable_agent_detects_success():
    agent = SolvableTaskAgent()
    assert agent.is_done("SUCCESS: report validated") is True


def test_impossible_agent_never_reports_success():
    agent = ImpossibleTaskAgent()
    assert agent.is_done("ERROR: DNS_RESOLUTION_FAILED") is False
    assert agent.is_done("FINAL_SUCCESS") is False


def test_llm_agent_can_be_instantiated_and_act_smoke():
    agent = llm_agent.LLMAgent(goal="probe tool loop")
    result = agent.act()
    assert isinstance(result, str)
    assert result


def test_llm_agent_uses_current_deterministic_groq_model(monkeypatch):
    captured = {}

    class FakeResponse:
        content = "ERROR: retry tool call"

    class FakeChatGroq:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def invoke(self, prompt):
            assert prompt
            return FakeResponse()

    monkeypatch.setattr(llm_agent, "ChatGroq", FakeChatGroq)

    result = llm_agent.LLMAgent(goal="probe", api_key="test-key").act()

    assert result == "ERROR: retry tool call"
    assert captured["model"] == "openai/gpt-oss-20b"
    assert captured["temperature"] == 0
    assert captured["groq_api_key"] == "test-key"
