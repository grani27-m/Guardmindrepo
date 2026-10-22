# GuardMind 🛡️
### Runtime Detection of Repeated Recorded Configurations in Autonomous AI-Agent Workflows

> **VIT Vellore — SCORE | BITE306L Theory of Computation**  
> **Team:** Rani Gupta (24BIT0543) · Swasti Sarangi (24BIT0127)  
> **Guide:** Dr. Pradeepa M | **TRL:** 4 — Validated in Laboratory Environment

---

## What is GuardMind?

GuardMind is a **runtime middleware guardrail** that wraps any autonomous AI agent and stops it the moment a repeated execution state is detected — replacing brittle step-cap timeouts with a structured, reproducible recurrence check grounded in **Linear Bounded Automaton (LBA) theory**.

```
Agent (LLM / LangChain / Groq)
        │  get_state() · act() · is_done()
        ▼
┌─────────────────────────────┐
│     run_with_guardrail      │  ← Middleware
│                             │
│  ┌── BoundedTape (n=4) ─┐  │  Keeps last n canonical observations
│  │  [NOT_FOUND, TIMEOUT, │  │
│  │   NOT_FOUND, TIMEOUT] │  │
│  └───────────────────────┘  │
│  ┌── seen_configurations ┐  │  Hash-set of (state, tape) keys
│  │  O(1) membership check│  │
│  └───────────────────────┘  │
└─────────────────────────────┘
        │
   ┌────┴────────────────────────┐
   │  SUCCESS                   │  Task completed
   │  HALTED_BY_LBA             │  Repeated configuration detected
   │  RAN_OUT_OF_STEPS          │  Step limit exhausted
   └────────────────────────────┘
```

---

## Why GuardMind?

| Problem | Existing Solutions | GuardMind |
|---|---|---|
| Agent stuck in period-3 loop (A→B→C→A→…) | Consecutive-repeat check **never detects it** | Detects at step `n + 3` ✅ |
| Genuine 15-step task killed by hard cap | Timeout at step 10 → task fails | Runs all 15 steps to SUCCESS ✅ |
| LLM phrasing varies across retries | Raw-text hash → state-leak bug | Canonical alphabet Σ → exact match ✅ |
| Multi-agent ping-pong deadlock | Invisible to per-agent monitors | Coordination guardrail detects it ✅ |

**Experimental results (scripted agents):** 40–70% step reduction vs. unguarded; 13/13 regression tests passing.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/grani27-m/GuardMind.git
cd GuardMind

# 2. Install
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt

# 3. Copy env template
cp .env.example .env        # Add your GROQ_API_KEY

# 4. Run tests
pytest -v

# 5. Launch demo
python api_server.py          # FastAPI  → http://localhost:8000
python chat_server.py         # Flask UI → http://localhost:5050
```

---

## Architecture (Five Layers)

```
AGENT LAYER        base_agent.py · mock_agent.py · llm_agent.py · interactive_agent.py
GUARDRAIL LAYER    tape.py · config_hasher.py · automaton.py
MIDDLEWARE LAYER   middleware.py  →  SUCCESS | HALTED_BY_LBA | RAN_OUT_OF_STEPS
SERVICE LAYER      api_server.py (FastAPI) · chat_server.py (Flask) · Streamlit demo
EVALUATION LAYER   scripts/ · report_assets/benchmark_results.csv
EXTENSIONS         adaptive_guardrail.py · near_duplicate_guardrail.py · coordination_guardrail.py
```

---

## Key Technical Contributions

1. **Bounded Observation Tape** — `collections.deque(maxlen=n)` recording the last *n* canonical observations; O(1) snapshot.
2. **Compound (state, tape) Configuration Key** — exact hash-set membership check; fires only on structural equality.
3. **Observation Canonicalization** — maps LLM free text → finite discrete token set Σ, resolving the state-leak bug.
4. **Agent-Agnostic Middleware** — any agent implementing `get_state / act / is_done` works without modification.
5. **Three Distinct Outcome Codes** — `SUCCESS`, `HALTED_BY_LBA`, `RAN_OUT_OF_STEPS` for differentiated downstream handling.
6. **Multi-Agent Coordination Guardrail** — applies bounded-tape recurrence to inter-agent handoff sequences.

**Configuration-space bound:** |C| ≤ q × n × m^n (control states × tape length × alphabet size^tape length).  
By the Pigeonhole Principle, any run exceeding this bound must revisit a *recorded* configuration.

---

## Project Reports

| Document | Description |
|---|---|
| [`PATENT_WORTHY_REPORT.md`](PATENT_WORTHY_REPORT.md) | Full patent-grade technical disclosure (13 sections, 7 claims, prior art, TRL assessment) |
| [`PROJECT_REPORT_AND_NOVELTY.md`](PROJECT_REPORT_AND_NOVELTY.md) | Novelty assessment with patentability review integration |
| [`docs/patent_claims.md`](docs/patent_claims.md) | Draft patent claims |
| [`docs/architecture.md`](docs/architecture.md) | Detailed architecture documentation |
| `report_assets/benchmark_results.csv` | 40-trial guarded vs. unguarded benchmark data |
| `report_assets/comparative_benchmark_results.csv` | TIMEOUT vs. REPEAT_COUNTER vs. LBA_GUARDRAIL comparison |

---

## Experimental Results Summary

### Guarded vs. Unguarded Execution (scripted ImpossibleTaskAgent, n=4 period=4)

| Tape Length n | Unguarded Steps | Guarded Steps | Reduction |
|---|---|---|---|
| 2 | 20 | 6 | 70% |
| 4 | 20 | 8 | 60% |
| 6 | 20 | 10 | 50% |
| 8 | 20 | 12 | 40% |

### Comparison with Alternative Stopping Methods

| Scenario | Timeout (cap=10) | Repeat Counter | GuardMind (n=4) |
|---|---|---|---|
| Genuine 15-step task | ❌ Kills at step 10 | ✅ Completes | ✅ Completes |
| Stuck, period 1 | Stops at 10 | Detects at 2 | Detects at 5 |
| Stuck, period 3 | Stops at 10 | ❌ Never detects | Detects at 7 |
| Stuck, period 5 | Stops at 10 | ❌ Never detects | Detects at 9 |

---

## Prior Art Differentiation

| Prior Art | Key Difference from GuardMind |
|---|---|
| Microsoft US20260017535A1 (2026) | Uses semantic embedding similarity (probabilistic); GuardMind uses exact compound-key equality (deterministic) |
| US 6,269,478 B1 — Siemens (2001) | OS process monitoring without bounded observation tape or canonical alphabet |
| AgentLoop (Zheng et al., 2026) | Task-completion heuristics; GuardMind fires on recorded-configuration recurrence only |
| LangChain GRAPH_RECURSION_LIMIT | Blind step counter; cannot distinguish progress from repetition |

---

## Tech Stack

`Python 3` · `FastAPI` · `Flask` · `Streamlit` · `LangChain` · `Groq` · `pytest` · `pandas` · `matplotlib`

---

## License

MIT License — see [LICENSE](LICENSE)

---

*VIT Vellore · SCORE · BITE306L · Academic Year 2026–2027*
