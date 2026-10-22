# GuardMind — TRL 4 Verification Document

> **Technology Readiness Level 4: Technology validated in laboratory environment**  
> This document provides independently verifiable evidence for all five TRL 4 requirements.  
> Every result listed here was produced by running the actual source code — not described retrospectively.

---

## Verification Metadata

| Field | Value |
|---|---|
| **Verification Date** | 2026-10-22 |
| **Verification Time** | 12:25:04 +05:30 (IST) |
| **Git Commit Hash** | `41e01d599f0ec9abc4f10aff1ff7603540fec6f9` |
| **Repository** | https://github.com/grani27-m/Guardmindrepo |
| **Python Version** | 3.14.2 |
| **OS Platform** | Microsoft Windows NT 10.0.26300.0 |
| **Test Framework** | pytest 9.1.1 |
| **Test Log File** | `trl4_test_log.txt` (in this repo) |
| **Benchmark Log File** | `trl4_benchmark_log.txt` (in this repo) |

---

## TRL 4 Requirement 1 — Versioned Source Code

**Status: ✅ VERIFIED**

The complete implementation is committed and publicly accessible at the commit hash above.

### Source modules and their roles:

| File | Role |
|---|---|
| `src/lba_guardrail/tape.py` | `BoundedTape` — `collections.deque(maxlen=n)` sliding observation window |
| `src/lba_guardrail/config_hasher.py` | `make_configuration(state, tape_snapshot)` — compound hashable key |
| `src/lba_guardrail/automaton.py` | `LBAGuardrail` — seen-set, recurrence detection, `q x n x m^n` bound |
| `src/lba_guardrail/middleware.py` | `run_with_guardrail` — agent-agnostic executor, three outcome codes |
| `src/lba_guardrail/metrics.py` | `RunMetrics` — steps, halt flag, wall-clock seconds, estimated cost |
| `src/lba_guardrail/agents/base_agent.py` | Abstract `Agent` interface: `get_state`, `act`, `is_done` |
| `src/lba_guardrail/agents/mock_agent.py` | `SolvableTaskAgent`, `ImpossibleTaskAgent` — deterministic scripted agents |
| `src/lba_guardrail/agents/llm_agent.py` | `LLMAgent` — live Groq/LangChain integration with canonical observation |
| `src/lba_guardrail/agents/interactive_agent.py` | `InteractiveLookupAgent` — canonicalization: raw LLM to FOUND/NOT_FOUND |
| `src/lba_guardrail/adaptive_guardrail.py` | `AdaptiveLBAGuardrail` — tape growth from `initial_length` to `max_tape_length` |
| `src/lba_guardrail/near_duplicate_guardrail.py` | `NearDuplicateGuardrail` — difflib similarity matching |
| `src/lba_guardrail/coordination_guardrail.py` | Multi-agent handoff sequence recurrence detection |
| `api_server.py` | FastAPI `POST /guardrail/check` service layer |
| `chat_server.py` | Flask chat UI on port 5050 |

**How to verify:**
```bash
git clone https://github.com/grani27-m/Guardmindrepo.git
git checkout 41e01d599f0ec9abc4f10aff1ff7603540fec6f9
```

---

## TRL 4 Requirement 2 — Reproducible Test Logs (13/13 Passing)

**Status: VERIFIED — Reproduced live on 2026-10-22 at 12:25:04 +05:30**

The following output was captured by running `pytest tests/ -v` against the committed source.
Full log saved to `trl4_test_log.txt`.

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
rootdir: .../Guardmindrepo
configfile: pytest.ini
plugins: anyio-4.15.1, langsmith-0.14.5
collecting ... collected 13 items

tests/test_agents.py::test_solvable_agent_detects_success              PASSED [  7%]
tests/test_agents.py::test_impossible_agent_never_reports_success       PASSED [ 15%]
tests/test_agents.py::test_llm_agent_can_be_instantiated_and_act_smoke PASSED [ 23%]
tests/test_agents.py::test_llm_agent_uses_current_deterministic_groq_model PASSED [ 30%]
tests/test_automaton.py::test_no_repeat_never_halts                    PASSED [ 38%]
tests/test_automaton.py::test_repeat_triggers_halt_at_second_repetition PASSED [ 46%]
tests/test_automaton.py::test_max_theoretical_configurations            PASSED [ 53%]
tests/test_middleware.py::test_solvable_agent_returns_success           PASSED [ 61%]
tests/test_middleware.py::test_impossible_agent_gets_halted             PASSED [ 69%]
tests/test_middleware.py::test_no_guardrail_runs_to_cap                 PASSED [ 76%]
tests/test_tape.py::test_append_keeps_recent_history_only              PASSED [ 84%]
tests/test_tape.py::test_snapshot_is_immutable_and_hashable            PASSED [ 92%]
tests/test_tape.py::test_identical_history_produces_equal_snapshots    PASSED [100%]

============================= 13 passed in 0.88s ==============================
```

**How to reproduce:**
```bash
pip install -r requirements.txt
pytest tests/ -v
```

### What each test verifies:

| Test | What it proves |
|---|---|
| `test_append_keeps_recent_history_only` | Tape discards oldest observation when at capacity n |
| `test_snapshot_is_immutable_and_hashable` | Snapshot is a hashable tuple -- valid Python dict/set key |
| `test_identical_history_produces_equal_snapshots` | Same state+tape always produces same key (determinism) |
| `test_no_repeat_never_halts` | Unique configurations never trigger a halt |
| `test_repeat_triggers_halt_at_second_repetition` | Repeated (state, tape) key triggers halt exactly once |
| `test_max_theoretical_configurations` | Formula q x n x m^n computes correctly |
| `test_solvable_agent_returns_success` | Middleware returns SUCCESS for completing agents |
| `test_impossible_agent_gets_halted` | Middleware returns HALTED_BY_LBA for looping agents |
| `test_no_guardrail_runs_to_cap` | Without guardrail, agent runs to max_steps (baseline) |
| `test_solvable_agent_detects_success` | Agent correctly reports task completion |
| `test_impossible_agent_never_reports_success` | Looping agent never self-reports success |
| `test_llm_agent_can_be_instantiated_and_act_smoke` | LLM agent class instantiates without error |
| `test_llm_agent_uses_current_deterministic_groq_model` | Groq model name is the expected deterministic version |

---

## TRL 4 Requirement 3 — Benchmark Data (Raw CSV)

**Status: VERIFIED — Reproduced live on 2026-10-22**

Both benchmarks were run fresh and CSVs regenerated. Full log in `trl4_benchmark_log.txt`.

### 3.1 Guarded vs. Unguarded Execution
**Source:** `report_assets/benchmark_results.csv` | **Script:** `scripts/run_benchmark.py`
Setup: `ImpossibleTaskAgent` (4-step cycle), `max_steps=20`, 5 trials per tape length.

| tape_length | guardrail_on | steps_taken | halted_by_lba |
|---|---|---|---|
| 2 | False | 20 (all 5 trials) | False |
| 2 | True  | 6  (all 5 trials) | True  |
| 4 | False | 20 (all 5 trials) | False |
| 4 | True  | 8  (all 5 trials) | True  |
| 6 | False | 20 (all 5 trials) | False |
| 6 | True  | 10 (all 5 trials) | True  |
| 8 | False | 20 (all 5 trials) | False |
| 8 | True  | 12 (all 5 trials) | True  |

Reduction: 40-70% fewer steps. Detection formula steps = n + period holds (period=4, n+4 verified in all 20 guarded trials, zero variance).

### 3.2 Comparative Method Benchmark
**Source:** `report_assets/comparative_benchmark_results.csv` | **Script:** `scripts/comparative_benchmark.py`

| Scenario | TIMEOUT (cap=10) | REPEAT_COUNTER | LBA_GUARDRAIL (n=4) |
|---|---|---|---|
| GenuineProgress (15 steps) | WRONG -- killed at step 10 | SUCCESS at 15 | SUCCESS at 15 |
| StuckAgent period=1 | Halts at 10 (blind) | Detects at step 2 | Detects at step 5 |
| StuckAgent period=3 | Halts at 10 (blind) | FAILED -- 50 steps, never detected | Detects at step 7 |
| StuckAgent period=5 | Halts at 10 (blind) | FAILED -- 50 steps, never detected | Detects at step 9 |

REPEAT_COUNTER false-negative rate: 50% on this test set. GuardMind: 0 false negatives, 0 false positives.

**How to reproduce:**
```bash
python scripts/run_benchmark.py
python scripts/comparative_benchmark.py
```

---

## TRL 4 Requirement 4 — Demonstration Artifacts

**Status: VERIFIED**

### 4.1 Automated Charts (regenerated 2026-10-22 12:26)

| Chart File | Size | Content |
|---|---|---|
| `report_assets/figures/steps_vs_tape_length.png` | 25 KB | Guarded vs. unguarded steps across tape lengths |
| `report_assets/figures/avg_steps_to_halt.png` | 14 KB | Average steps to halt per tape length |
| `report_assets/figures/comparative_chart.png` | 91 KB | Three-method comparison bar chart |

Generate with:
```bash
python scripts/generate_report_charts.py
python scripts/make_comparative_chart.py
```

### 4.2 Running Services

| Service | Command | URL |
|---|---|---|
| FastAPI REST API | `python api_server.py` | http://localhost:8000 |
| Flask Chat UI | `python chat_server.py` | http://localhost:5050 |
| Streamlit Demo | `streamlit run demo/demo_streamlit_app.py` | http://localhost:8501 |

**API verification call:**
```bash
curl -X POST http://localhost:8000/guardrail/check \
  -H "Content-Type: application/json" \
  -d '{"goal":"trl4_demo","max_steps":20,"tape_length":4,"agent_type":"impossible"}'
```
Expected: `{"outcome": "HALTED_BY_LBA", "steps_taken": 8, "halted": true}`

### 4.3 Demo Scripts

| Script | Demonstrates |
|---|---|
| `demo/demo_protected.py` | Side-by-side guarded vs. unguarded on impossible task |
| `demo/demo_baseline_failure.py` | Unguarded agent running to step cap (baseline) |
| `demo/demo_interactive.py` | Interactive product-lookup agent with guardrail |
| `demo/demo_llm_protected.py` | Live Groq LLM with guardrail (requires GROQ_API_KEY) |
| `demo/demo_real_search.py` | Real web-search agent with guardrail |

---

## TRL 4 Requirement 5 — Integrated Laboratory Prototype

**Status: VERIFIED**

The prototype is a fully integrated stack -- not isolated scripts:

```
Service Layer  (api_server.py / chat_server.py)
       |
       v  POST /guardrail/check
Middleware     (run_with_guardrail in middleware.py)
       |
       v  get_state -> act -> is_done
Agent          (LLMAgent / MockAgent / InteractiveAgent)
       |
       v  canonical observation token
LBAGuardrail   (automaton.py)
       |
       v  tape.append -> config_hasher -> seen-set lookup
BoundedTape + seen_configurations
       |
       v
Outcome: SUCCESS | HALTED_BY_LBA | RAN_OUT_OF_STEPS
```

Integration evidence:
- `api_server.py` calls `run_with_guardrail` (middleware) -- `LBAGuardrail` (automaton) -- any `Agent`
- `tests/test_middleware.py` tests the full stack end-to-end (not individually mocked layers)
- `demo/demo_interactive.py` runs the complete integration with live user input
- `chat_server.py` exposes the full stack through a browser UI at port 5050

**Full prototype quick-start:**
```bash
git clone https://github.com/grani27-m/Guardmindrepo.git
cd Guardmindrepo
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
cp .env.example .env              # add GROQ_API_KEY for live LLM features
pytest tests/ -v                  # verify: 13 passed
python demo/demo_protected.py     # run integrated demo
```

---

## TRL 4 Summary Checklist

| TRL 4 Requirement | Evidence | Status |
|---|---|---|
| Integrated laboratory prototype | Full stack: api_server -> middleware -> automaton -> tape | VERIFIED |
| Versioned source code | Git commit `41e01d5` on https://github.com/grani27-m/Guardmindrepo | VERIFIED |
| Reproducible test logs | `trl4_test_log.txt` -- 13/13 passed, 0.88s, dated 2026-10-22 | VERIFIED |
| Benchmark data | `report_assets/benchmark_results.csv` (40 trials), `comparative_benchmark_results.csv` | VERIFIED |
| Demonstration artifacts | 3 charts (PNG), FastAPI service, Flask UI, Streamlit app, 5 demo scripts | VERIFIED |

All five TRL 4 verification requirements are satisfied by independently reproducible evidence tied to a public, immutable git commit (`41e01d599f0ec9abc4f10aff1ff7603540fec6f9`).

---

*Document generated: 2026-10-22 | GuardMind v1.0 | VIT Vellore SCORE BITE306L*
