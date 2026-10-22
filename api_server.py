"""FastAPI backend for the LBA guardrail project."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from lba_guardrail.agents.llm_agent import LLMAgent
from lba_guardrail.agents.mock_agent import ImpossibleTaskAgent, SolvableTaskAgent
from lba_guardrail.automaton import LBAGuardrail
from lba_guardrail.middleware import HALTED_BY_LBA, RAN_OUT_OF_STEPS, SUCCESS, run_with_guardrail

load_dotenv()

app = FastAPI(title="LBA Agent Guardrail API", version="1.0.0")


class GuardrailRequest(BaseModel):
    goal: str = Field(default="loop_detection_demo")
    max_steps: int = Field(default=20, ge=1, le=200)
    tape_length: int = Field(default=4, ge=1, le=32)
    agent_type: str = Field(default="impossible", pattern="^(impossible|solvable|llm)$")


class ExecutionResponse(BaseModel):
    result: str
    halted: bool
    halt_reason: str | None = None
    agent_type: str
    steps_taken: int | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "lba-guardrail-api"}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "LBA Agent Guardrail API is running"}


@app.post("/guardrail/check", response_model=ExecutionResponse)
def check_guardrail(payload: GuardrailRequest) -> ExecutionResponse:
    if payload.agent_type == "solvable":
        agent = SolvableTaskAgent(goal=payload.goal)
    elif payload.agent_type == "llm":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="GROQ_API_KEY is not configured")
        agent = LLMAgent(goal=payload.goal, api_key=api_key)
    else:
        agent = ImpossibleTaskAgent(goal=payload.goal)

    guardrail = LBAGuardrail(tape_length=payload.tape_length)
    result = run_with_guardrail(agent, guardrail, max_steps=payload.max_steps)

    if result == HALTED_BY_LBA:
        steps_taken = len(guardrail.history)
    elif result == SUCCESS:
        steps_taken = len(guardrail.history) + 1
    else:
        steps_taken = payload.max_steps

    return ExecutionResponse(
        result=result,
        halted=guardrail.halted,
        halt_reason=guardrail.halt_reason,
        agent_type=payload.agent_type,
        steps_taken=steps_taken,
    )


@app.post("/agent/run")
def run_agent(payload: GuardrailRequest) -> dict[str, Any]:
    if payload.agent_type == "llm":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=400, detail="GROQ_API_KEY is not configured")
        agent = LLMAgent(goal=payload.goal, api_key=api_key)
    elif payload.agent_type == "solvable":
        agent = SolvableTaskAgent(goal=payload.goal)
    else:
        agent = ImpossibleTaskAgent(goal=payload.goal)

    guardrail = LBAGuardrail(tape_length=payload.tape_length)
    result = run_with_guardrail(agent, guardrail, max_steps=payload.max_steps)
    return {
        "result": result,
        "halted": guardrail.halted,
        "halt_reason": guardrail.halt_reason,
        "agent_type": payload.agent_type,
        "steps_taken": len(guardrail.history) if guardrail.history else payload.max_steps,
    }


@app.get("/guardrail/demo")
def demo() -> dict[str, Any]:
    agent = ImpossibleTaskAgent(goal="guarded_loop_detect")
    guardrail = LBAGuardrail(tape_length=4)
    result = run_with_guardrail(agent, guardrail, max_steps=10)
    return {
        "result": result,
        "halted": guardrail.halted,
        "halt_reason": guardrail.halt_reason,
        "status": "ok",
        "success": result in {SUCCESS, HALTED_BY_LBA, RAN_OUT_OF_STEPS},
    }
