# Project Blueprint
## Deterministic Infinite Loop Prevention in Autonomous AI Agents Using Linear Bounded Automata (LBA)

This document is the single source of truth for building this project. Feed sections
of it to whichever AI coding tool you're using (Claude Code, Copilot, Antigravity,
Claude chat) — each section is self-contained enough to hand off as a task.

---

## 1. Project Overview

**One-line pitch:** A middleware "circuit breaker" that wraps any autonomous AI agent's
execution loop, models the agent's bounded action-history as a Linear Bounded Automaton
(LBA), and mathematically proves — not guesses — when the agent is stuck in an infinite
loop, so it can be safely terminated before it burns compute/API cost.

**Core TOC claim:** The Halting Problem is undecidable for a general Turing Machine
(unrestricted agent memory). But an LBA — a Turing Machine restricted to a tape of
length linear in the input — has a **finite** number of possible configurations
(`q × n × m^n`). Therefore, if the agent's execution history is bounded to a fixed
window, a repeated `(state, tape)` configuration is formal, mathematical proof of an
infinite loop, not a heuristic guess.

**Deliverables required by course:**
1. Phase 1 — topic registered (already done)
2. Phase 2 — working prototype + live demo
3. Phase 3 — final report (10 sections, see `docs/phase3_report_outline.md`)

---

## 2. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.10+ | Fast to prototype, great for both automata logic and AI/LLM glue |
| Agent framework | LangChain (or raw API calls) | Standard "autonomous agent" pattern (tool-calling loop) |
| LLM provider | Groq (free/fast) or OpenAI | Groq has a generous free tier — good for a student demo |
| Testing | `pytest` | Standard, minimal setup |
| Charts / experimental validation | `matplotlib`, `pandas` | For Phase 3 Section 8 graphs |
| Optional UI | `streamlit` or `gradio` | Nice visual live-demo instead of terminal output |
| Env management | `venv` + `requirements.txt` | Keep it simple — no need for poetry/conda |
| Version control | Git + GitHub (private repo is fine) | Lets you use Claude Code / Copilot properly, and gives you commit history as "proof of work" for your report |

You do **not** need: Docker, Kubernetes, a database, a frontend framework, or cloud
deployment. Keep this lean — a bloated stack will hurt you, not help you (see your
professor's note: "the best project is not necessarily the most complex one").

---

## 3. Full Directory Structure

```
lba-agent-guardrail/
├── README.md                        # what the project is, how to run it
├── PROJECT_BLUEPRINT.md             # this file
├── LICENSE                          # MIT is fine for a student project
├── requirements.txt
├── .gitignore
├── .env.example                     # template for API keys (never commit real .env)
├── pyproject.toml                   # optional, for packaging src/ properly
│
├── src/
│   └── lba_guardrail/
│       ├── __init__.py
│       ├── tape.py                  # BoundedTape class (the LBA's finite memory)
│       ├── automaton.py             # LBAGuardrail class (the core invention)
│       ├── config_hasher.py         # turns (state, tape) into a hashable configuration
│       ├── middleware.py            # wraps ANY agent loop with the guardrail
│       ├── metrics.py               # tracks steps, tokens, cost, halts for benchmarking
│       │
│       └── agents/
│           ├── __init__.py
│           ├── base_agent.py        # abstract Agent interface (step() method)
│           ├── mock_agent.py        # deterministic offline agent (no API needed)
│           └── llm_agent.py         # real LangChain/LLM-backed autonomous agent
│
├── demo/
│   ├── demo_baseline_failure.py     # agent WITHOUT guardrail -> loops forever
│   ├── demo_protected.py            # agent WITH guardrail -> self-halts
│   └── demo_streamlit_app.py        # optional visual dashboard for live demo
│
├── tests/
│   ├── test_tape.py
│   ├── test_automaton.py
│   ├── test_middleware.py
│   └── test_agents.py
│
├── notebooks/
│   └── benchmarking.ipynb           # run experiments, produce graphs for report
│
├── scripts/
│   ├── run_benchmark.py             # automates: baseline vs protected, N trials
│   └── generate_report_charts.py    # outputs PNGs into report_assets/figures/
│
├── report_assets/
│   ├── architecture_diagram.png     # block diagram for Section 6
│   ├── benchmark_results.csv        # raw data for Section 8
│   └── figures/                     # generated charts
│
└── docs/
    ├── phase1_topic_submission.md   # already done — keep for records
    ├── phase3_report_outline.md     # section-by-section report skeleton
    ├── patent_claims.md             # draft claims for Section 9
    └── architecture.md              # written explanation of the design
```

---

## 4. File-by-File Responsibility Breakdown

### `src/lba_guardrail/tape.py`
- `BoundedTape` class: a fixed-length `collections.deque`.
- Holds the last `k` observations/tool-results from the agent.
- This **is** the LBA's tape restricted to a linear bound on input length.
- Methods: `append(observation)`, `snapshot() -> tuple`.

### `src/lba_guardrail/config_hasher.py`
- Pure function(s) that take `(state, tape_snapshot)` and return an immutable,
  hashable key — e.g. `(state_string, tuple(tape))`.
- Keep this separate from `automaton.py` so it's independently unit-testable and
  so you can swap in a smarter hashing strategy later (e.g. semantic similarity
  instead of exact string match) without touching the core automaton logic.

### `src/lba_guardrail/automaton.py`
- `LBAGuardrail` class — the heart of the invention.
- Holds: `tape: BoundedTape`, `seen_configurations: set`, `halted: bool`.
- `step(state, observation) -> bool`: returns `False` the instant a configuration
  repeats (loop proven), `True` otherwise.
- `max_theoretical_configurations(num_states, alphabet_size) -> int`: implements
  `q × n × m^n` — this is your formal decidability proof, used directly in your
  Phase 3 report.

### `src/lba_guardrail/middleware.py`
- `run_with_guardrail(agent, guardrail, max_steps) -> ExecutionResult` — a generic
  wrapper that works with ANY object implementing the `base_agent.Agent` interface.
- This generality matters for your patent claim: you're not hard-coding one agent,
  you're patenting a **method** applicable to any agent architecture.

### `src/lba_guardrail/metrics.py`
- Tracks per-run: steps taken, (simulated or real) tokens/cost, whether halted by
  guardrail, wall-clock time.
- Used by `scripts/run_benchmark.py` to produce your Section 8 experimental data.

### `src/lba_guardrail/agents/base_agent.py`
- Abstract class defining the contract every agent must satisfy:
  ```python
  class Agent(ABC):
      @abstractmethod
      def get_state(self) -> str: ...
      @abstractmethod
      def act(self) -> str:  # returns an observation
          ...
      @abstractmethod
      def is_done(self, observation: str) -> bool: ...
  ```

### `src/lba_guardrail/agents/mock_agent.py`
- A deterministic, offline agent that simulates both a solvable task and an
  impossible task (cycles through fixed fallback errors).
- **Use this for your live classroom demo** — zero risk of API downtime, zero cost,
  100% reproducible in front of your professor.

### `src/lba_guardrail/agents/llm_agent.py`
- A real LangChain-based agent that calls an actual LLM with tool access
  (e.g. a web-search tool, a calculator tool).
- Use this in your report / video demo to show the guardrail works on a genuine
  model, not just a toy — this is what makes the patent claim credible.
- Needs `GROQ_API_KEY` or `OPENAI_API_KEY` from `.env`.

### `demo/demo_baseline_failure.py`
- Runs the impossible-task agent with NO guardrail. Prints the raw loop.
- This is what you show FIRST to the professor — "here's the problem."

### `demo/demo_protected.py`
- Same impossible-task agent, WITH the guardrail wrapped around it.
- Shows the exact step where the repeated configuration is detected and the
  agent halts, with the configuration printed out as proof.

### `demo/demo_streamlit_app.py` (optional but recommended)
- A simple Streamlit page: a "Run Agent" button, a live log panel, and a red
  banner that appears when the LBA halts the agent. Much more impressive in a
  live demo than a terminal.

### `scripts/run_benchmark.py`
- Runs baseline vs. protected agent N times each, across different
  `tape_length` values, and saves results to `report_assets/benchmark_results.csv`.
- This is your **experimental validation** — the thing markers specifically look for.

### `scripts/generate_report_charts.py`
- Reads the CSV and produces 2–3 matplotlib charts:
  1. Steps-to-halt: baseline (runs to cap) vs. protected (halts early)
  2. Tape length vs. steps-to-detect
  3. Simulated cost/tokens saved

---

## 5. Core Algorithm Spec (pseudocode — implement this exactly)

```
class BoundedTape:
    tape = deque(maxlen = TAPE_LENGTH)

    append(observation):
        tape.append(observation)

    snapshot():
        return tuple(tape)


class LBAGuardrail:
    tape = BoundedTape()
    seen_configurations = empty set
    halted = False

    step(state, observation):
        tape.append(observation)
        config = (state, tape.snapshot())

        if config in seen_configurations:
            halted = True
            return False        # LOOP PROVEN -> caller must stop the agent

        seen_configurations.add(config)
        return True              # safe to continue


run_with_guardrail(agent, guardrail, max_steps):
    for i in 1..max_steps:
        state = agent.get_state()
        observation = agent.act()

        if agent.is_done(observation):
            return SUCCESS

        if guardrail.step(state, observation) == False:
            return HALTED_BY_LBA   # <-- your invention firing

    return RAN_OUT_OF_STEPS  # only happens if guardrail is off (baseline)
```

Keep `automaton.py` under ~80 lines. If any AI tool tries to over-engineer this
class (adding threading, async, plugin systems, etc.) — reject it. The whole
point of the patent claim is that the core logic is simple, provable, and formal.

---

## 6. Development Roadmap

### Week 1 — Core Automata Logic (no AI/LLM involved yet)
- [ ] Set up repo, venv, `requirements.txt`, folder structure
- [ ] Implement `tape.py`, `config_hasher.py`, `automaton.py`
- [ ] Write `tests/test_tape.py` and `tests/test_automaton.py`
- [ ] Manually feed the `LBAGuardrail` a hardcoded sequence of states/observations
      that repeats, and confirm it halts at the correct step
- **Milestone:** `pytest` passes, you can explain `q × n × m^n` out loud without notes

### Week 2 — Agent Simulation
- [ ] Implement `base_agent.py` and `mock_agent.py`
- [ ] Implement `middleware.py` (`run_with_guardrail`)
- [ ] Build `demo/demo_baseline_failure.py` and `demo/demo_protected.py`
- **Milestone:** Both demo scripts run end-to-end and produce the expected
  contrasting outputs (baseline loops to cap; protected self-halts)

### Week 3 — Real LLM Integration
- [ ] Sign up for a free Groq API key (or OpenAI)
- [ ] Implement `llm_agent.py` using LangChain with 1–2 real tools
      (e.g. a web-search tool that can plausibly fail/loop)
- [ ] Confirm the SAME `LBAGuardrail` class (unmodified) works on this real agent
- **Milestone:** You can demo the guardrail catching a loop in a REAL AI agent,
  not just the mock one — this is what makes Phase 2 demonstration strong

### Week 4 — Benchmarking & Report Prep
- [ ] Implement `scripts/run_benchmark.py` and `generate_report_charts.py`
- [ ] Run experiments across at least 3 different `tape_length` values
- [ ] Generate the 2–3 charts for Section 8
- [ ] Draw the architecture/block diagram for Section 6 (draw.io / Excalidraw is fine)
- [ ] Draft `docs/patent_claims.md`
- **Milestone:** All raw material for the Phase 3 report exists as files, not
  just in your head

### Week 5 (buffer) — Polish + Report Writing
- [ ] Write the actual Phase 3 report using `docs/phase3_report_outline.md`
- [ ] Rehearse the live demo (baseline fails → protected catches it)
- [ ] Optional: wire up `demo_streamlit_app.py` if you want a visual demo

---

## 7. Environment Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy the env template and add your key (only needed for llm_agent.py)
cp .env.example .env
# then edit .env and add GROQ_API_KEY=... or OPENAI_API_KEY=...

# 4. Run tests
pytest

# 5. Run the demos
python demo/demo_baseline_failure.py
python demo/demo_protected.py
```

`requirements.txt` (starting point — trim what you don't use):
```
langchain
langchain-groq        # or: openai
python-dotenv
pytest
matplotlib
pandas
streamlit             # optional, only if you build the visual demo
```

---

## 8. How to Split Work Across AI Tools

You mentioned using multiple tools — here's a sensible division so they don't
step on each other:

| Tool | Best used for |
|---|---|
| **Claude (chat)** | Architecture decisions, writing the report sections, explaining TOC concepts back to you in plain language, reviewing code another tool wrote for correctness against the pseudocode in Section 5 |
| **Claude Code / Antigravity (agentic IDE)** | Actually scaffolding and writing the repo end-to-end from this blueprint — point it at this file and say "implement Section 3–5 exactly as specified" |
| **Copilot** | Fast autocomplete while you hand-write test cases or tweak the mock agent's fallback strings |

**Important:** whichever tool writes `automaton.py`, paste it back into a
Claude chat and ask it to verify the logic matches Section 5's pseudocode
exactly, and that `max_theoretical_configurations` correctly implements
`q × n × m^n`. This is the one file where correctness matters for your
patent claim — don't let an agentic tool "improve" it into something you
can't explain on the spot to your professor.

---

## 9. Testing & Validation Plan

Minimum tests to have before Phase 2 demo:

1. `test_automaton.py`
   - A sequence with no repeats never halts early
   - A sequence with a deliberate repeat halts at the correct step
   - `max_theoretical_configurations` returns the correct value for known inputs
2. `test_middleware.py`
   - `run_with_guardrail` returns `SUCCESS` for a solvable mock agent
   - Returns `HALTED_BY_LBA` for the impossible mock agent
3. `test_agents.py`
   - Mock agent's `is_done` correctly detects the SUCCESS state
   - (If using `llm_agent.py`) a smoke test that it can be instantiated and
     called once — don't unit-test live API responses, they're non-deterministic

---

## 10. Report & Patent Documentation Checklist

Map directly onto the Phase 3 report format your professor gave you:

- [ ] **Section 3** (Prior art table) — cite XGrammar / grammar-constrained
      decoding papers as adjacent work, and explicitly state your research gap:
      those use CFG/PDA for *output formatting*, you use LBA for *execution
      loop decidability* — a different automaton class solving a different problem
- [ ] **Section 6** (Working principle) — use the architecture diagram +
      pseudocode from Section 5 of this document
- [ ] **Section 7** (Detailed description) — walk through each file in Section 4
- [ ] **Section 8** (Experimental validation) — insert the charts from
      `scripts/generate_report_charts.py`
- [ ] **Section 9** (Patent claims) — draft in `docs/patent_claims.md`, core
      claims:
      1. A method of mapping an autonomous agent's execution history onto a
         bounded (LBA) tape structure
      2. A method of proving loop termination via configuration-repetition
         detection over that bounded tape
      3. A middleware architecture applying this method transparently to
         arbitrary agent implementations
- [ ] **Section 10** (TRL) — this prototype sits at **TRL 3** (analytical and
      experimental proof of concept)

---

## 11. Starter Scaffold

A matching starter folder (`lba-agent-guardrail-starter/`) with this exact
structure and skeleton files (docstrings + `TODO`s, no full implementation)
has been generated alongside this blueprint as a zip — unzip it and hand
individual files to your coding tool of choice, one at a time, following the
Week 1–5 roadmap above.
