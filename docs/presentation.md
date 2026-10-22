# GuardMind — LBA Agent Guardrail
## Project Presentation & Documentation

**Course:** Theory of Computation (TOC)
**Project Phase:** Phase 3 — Implementation & Demonstration
**Student:** Rani Gupta and Swasti 
**System:** GuardMind AI Agent with Linear Bounded Automaton Safety Layer

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Theory of Computation Foundation](#2-theory-of-computation-foundation)
3. [System Architecture](#3-system-architecture)
4. [The LBA Guardrail — How It Works](#4-the-lba-guardrail--how-it-works)
5. [The Pigeonhole Principle in Action](#5-the-pigeonhole-principle-in-action)
6. [Implementation Details](#6-implementation-details)
7. [Comparative Benchmark Results](#7-comparative-benchmark-results)
8. [Advanced Extensions](#8-advanced-extensions)
9. [Live Demo Walkthrough](#9-live-demo-walkthrough)
10. [Conclusion](#10-conclusion)

---

## 1. Problem Statement

### The Real-World Challenge

Modern AI agents (like ChatGPT plugins, customer service bots, and search agents) are designed to be **persistent** — when a task fails, they retry it. This is correct behavior for solvable problems.

**But what happens when the problem is unsolvable?**

```
Agent: "I'll search for order-XYZ"   → NOT FOUND → retries
Agent: "I'll search for order-XYZ"   → NOT FOUND → retries
Agent: "I'll search for order-XYZ"   → NOT FOUND → retries
Agent: "I'll search for order-XYZ"   → NOT FOUND → retries
... forever, wasting compute and money ...
```

This is the **infinite loop problem** in AI agents. Without a safety mechanism:
- The agent wastes thousands of API calls
- It costs real money (every LLM call is billed)
- The user gets no response
- The system hangs

### Existing Solutions and Their Failures

| Solution | How It Works | Why It Fails |
|---|---|---|
| **Timeout** | Kill agent after N seconds | Kills legitimate slow tasks too (false positives) |
| **Step Counter** | Kill after N steps | Arbitrary — too high wastes resources, too low kills valid work |
| **Repeat Counter** | Stop if same output twice in a row | Fooled by alternating loops: A→B→A→B→... (never same consecutively) |

> **None of these provide a mathematical guarantee. They are heuristics that can fail.**

### Our Solution

A **Linear Bounded Automaton (LBA) Guardrail** — a mathematically proven, deterministic method to detect infinite loops in AI agents, grounded in Theory of Computation.

---

## 2. Theory of Computation Foundation

### 2.1 Formal Language Theory

Our project applies core TOC concepts:

| TOC Concept | How We Use It |
|---|---|
| **Finite Automaton** | The LBA guardrail IS a finite-state machine |
| **Bounded Tape** | Agent's observation history stored in fixed-length tape |
| **Configuration** | (state, tape) pair — the complete snapshot of the system |
| **Decidability** | Loop detection is **decidable** given bounded memory |
| **Pigeonhole Principle** | Mathematical proof that finite configurations must repeat |

### 2.2 Why Bounded Memory Makes This Decidable

The Halting Problem tells us: *for a Turing machine with infinite tape, we CANNOT decide if it halts.*

But our guardrail uses a **bounded tape** — finite memory. This changes everything:

```
Turing Machine (infinite tape)  →  Halting Problem UNDECIDABLE
Linear Bounded Automaton        →  Halting Problem DECIDABLE (finite configs)
```

This is the key insight: **by restricting the tape to a finite length, we make loop detection mathematically solvable.**

### 2.3 Configuration Space

For a guardrail with:
- `tape_length = 4`
- `n` possible observation values (e.g., FOUND, NOT_FOUND = 2)
- `s` possible agent states

The total configuration space = **s × nᵏ** (where k = tape_length)

Once the agent has run more steps than this space allows, by the Pigeonhole Principle, **a configuration MUST repeat — proving a loop.**

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GuardMind System                         │
│                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   User   │───▶│  Chat UI     │───▶│  Flask API       │  │
│  │  (Chat)  │    │  (HTML/CSS)  │    │  chat_server.py  │  │
│  └──────────┘    └──────────────┘    └────────┬─────────┘  │
│                                               │             │
│                        ┌──────────────────────┤             │
│                        │                      │             │
│               ┌────────▼──────┐    ┌──────────▼─────────┐  │
│               │  Groq LLM     │    │  LBA Guardrail     │  │
│               │  (Conversation│    │  (Loop Detection)  │  │
│               │   & Lookup)   │    │                    │  │
│               └───────────────┘    │  ┌──────────────┐  │  │
│                                    │  │ BoundedTape  │  │  │
│                                    │  │ (tape_len=4) │  │  │
│                                    │  └──────────────┘  │  │
│                                    │  ┌──────────────┐  │  │
│                                    │  │ConfigHasher  │  │  │
│                                    │  │(seen configs)│  │  │
│                                    │  └──────────────┘  │  │
│                                    └────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Message Flow

```
User sends "search for xyz-999"
         │
         ▼
Intent Detector (keyword match: "search for" → LOOKUP)
         │
         ├──▶ Groq LLM ──▶ Natural language reply
         │
         └──▶ LBA Guardrail + Lookup Agent
                    │
                    │  Step 1: state="query=xyz-999|last=START"
                    │           obs="NOT_FOUND" → tape=("NOT_FOUND",)
                    │  Step 2: state="query=xyz-999|last=NOT_FOUND"
                    │           obs="NOT_FOUND" → tape=("NOT_FOUND","NOT_FOUND")
                    │  ...
                    │  Step 5: SAME config as Step 4 → LOOP PROVEN
                    │
                    ▼
         Guardrail card shown with tape visualization
```

---

## 4. The LBA Guardrail — How It Works

### 4.1 Core Algorithm

```python
def step(self, state: str, observation: str) -> bool:
    """
    Returns True  → agent may continue
    Returns False → HALT: infinite loop mathematically proven
    """
    self.tape.append(observation)           # update bounded tape
    config = (state, self.tape.snapshot())  # create (state, tape) pair
    
    if config in self.seen_configurations:  # Pigeonhole check
        self.halted = True
        self.halt_reason = "Repeated configuration detected — loop proven"
        return False
    
    self.seen_configurations.add(config)    # record for future comparison
    return True
```

### 4.2 Why No Step Counter in `get_state()`

> **Critical Design Decision:** The agent's `get_state()` must NOT include a step counter.

If `get_state()` returns `"query=xyz-999|step=5"`, every step produces a unique configuration, defeating the entire guardrail. The state must represent the agent's **actual cognitive situation**, not its iteration count.

This was a real bug discovered and fixed during development — a key learning about formal state representation.

### 4.3 Canonical Observations

The guardrail tape only receives **canonical tokens** (`FOUND` / `NOT_FOUND`), never raw LLM text.

```
LLM says: "I'll retry the search now."     → tape sees: "NOT_FOUND"
LLM says: "Retrying the lookup..."          → tape sees: "NOT_FOUND"
LLM says: "Let me try again."              → tape sees: "NOT_FOUND"
```

This ensures the guardrail is not confused by natural language variation. The **display** shown to the human is the rich LLM text. The **tape** always gets the canonical value.

---

## 5. The Pigeonhole Principle in Action

### Statement

> If there are **N** pigeonholes and **N+1** pigeons, at least one pigeonhole must contain two pigeons.

### Applied to Our System

- **Pigeonholes** = all possible (state, tape) configurations (finite, bounded)
- **Pigeons** = each step the agent takes

Once the agent has taken more steps than there are configurations, **at least one configuration must repeat**. When it does, the agent is provably in a cycle and will never terminate.

### Detection Formula

```
steps_to_detect = tape_length + period

For tape_length=4 and period=1 (same obs every step):
  steps_to_detect = 4 + 1 = 5   ✓ (verified in our benchmark)

For tape_length=4 and period=3 (A,B,C,A,B,C,...):
  steps_to_detect = 4 + 3 = 7   ✓ (verified in our benchmark)
```

### Verified Empirically

```
period=1  tape_length=4  → detected at step 5   (formula: 4+1=5,  match=YES ✓)
period=3  tape_length=4  → detected at step 7   (formula: 4+3=7,  match=YES ✓)
period=5  tape_length=4  → detected at step 9   (formula: 4+5=9,  match=YES ✓)
period=9  tape_length=4  → detected at step 13  (formula: 4+9=13, match=YES ✓)
```

---

## 6. Implementation Details

### 6.1 File Structure

```
lba-agent-guardrail-starter/
├── src/lba_guardrail/
│   ├── tape.py                    ← BoundedTape (fixed-length deque)
│   ├── automaton.py               ← LBAGuardrail (core algorithm)
│   ├── config_hasher.py           ← Configuration hashing
│   ├── middleware.py              ← run_with_guardrail()
│   ├── metrics.py                 ← RunMetrics dataclass
│   ├── near_duplicate_guardrail.py ← Tier 2: semantic matching
│   ├── adaptive_guardrail.py      ← Tier 2: adaptive tape length
│   ├── coordination_guardrail.py  ← Tier 3: multi-agent coordination
│   └── agents/
│       ├── base_agent.py          ← Agent ABC
│       ├── llm_agent.py           ← Groq LLM agent
│       ├── mock_agent.py          ← Test agents
│       ├── interactive_agent.py   ← Knowledge-base lookup agent
│       └── real_search_agent.py   ← DuckDuckGo web search agent
├── demo/
│   ├── chat_ui/index.html         ← Premium chat interface
│   └── demo_interactive_selftest.py
├── scripts/
│   ├── run_benchmark.py           ← Baseline vs protected benchmark
│   ├── comparative_benchmark.py   ← LBA vs timeout vs repeat-counter
│   ├── make_comparative_chart.py  ← Chart generation
│   └── generate_architecture_diagram.py
├── report_assets/
│   ├── benchmark_results.csv
│   ├── comparative_benchmark_results.csv
│   ├── pigeonhole_diagram.png
│   └── figures/comparative_chart.png
├── tests/                         ← 13 automated tests (all passing)
├── docs/phase3_report.md          ← Full academic report
├── chat_server.py                 ← Flask chat backend
└── api_server.py                  ← FastAPI REST backend
```

### 6.2 Key Technologies

| Component | Technology | Why |
|---|---|---|
| LLM Backend | Groq API (llama/GPT) | Free, fast, real AI responses |
| Chat Backend | Flask + Flask-CORS | Lightweight Python server |
| Frontend | HTML5 / CSS3 / Vanilla JS | No framework overhead, full control |
| Testing | pytest (13 tests) | Automated regression coverage |
| Benchmarks | Python + matplotlib | Visual proof of superiority |

### 6.3 Test Suite — 13 Tests, All Passing

```
tests/test_tape.py          → BoundedTape append, snapshot, overflow
tests/test_automaton.py     → Guardrail fires on repeat, allows progress
tests/test_middleware.py    → run_with_guardrail() integration
tests/test_agents.py        → SolvableTask, ImpossibleTask behavior
tests/test_api.py           → FastAPI endpoint responses
```

---

## 7. Comparative Benchmark Results

### The Key Result

| Method | GenuineProgress (15 steps) | StuckAgent period=1 | StuckAgent period=3 | StuckAgent period=5 |
|---|---|---|---|---|
| **TIMEOUT(cutoff=10)** | ❌ WRONG — killed at step 10 | Halts (blind) | Halts (blind) | Halts (blind) |
| **REPEAT_COUNTER** | ✅ Correct | ✅ Detected at step 2 | ❌ FAILED — never detected | ❌ FAILED — never detected |
| **LBA_GUARDRAIL** | ✅ Correct | ✅ Detected at step 5 | ✅ Detected at step 7 | ✅ Detected at step 9 |

### Summary

```
TIMEOUT(cutoff=10)  : detected 3/3 stuck scenarios — but WRONG on genuine task
REPEAT_COUNTER      : detected 1/3 stuck scenarios — FAILS on period > 1 loops
LBA_GUARDRAIL       : detected 3/3 stuck scenarios — CORRECT on everything
```

> **The LBA Guardrail is the only method that is both correct (no false positives on genuine work) and complete (catches all loop periods).**

---

## 8. Advanced Extensions

### Tier 2: Near-Duplicate Matching
**Problem:** Real LLMs vary their phrasing slightly each retry. Exact string match may take longer.

**Solution:** `NearDuplicateGuardrail` uses `difflib` similarity scoring.

**Result:** Detected loop at step **5** vs exact-match at step **12** — 58% faster.

### Tier 2: Adaptive Tape Length
**Key finding:** `steps_to_detect = tape_length + period` — a **smaller tape detects loops faster**.

**Also found:** `tape_length=1` causes false positives on legitimate polling agents (kills healthy agents). Adaptive growth starts small and grows to avoid this.

### Tier 3: Multi-Agent Coordination Guardrail
**Problem:** In multi-agent systems, no single agent loops — but agents can ping-pong tasks between each other forever.

**Solution:** `CoordinationGuardrail` watches the **sequence of handoffs** across agents.

**Result:**
```
Scenario A (normal): Router → Billing → RESOLVED in 2 hops ✅
Scenario B (loop):   Router→Billing→Router→Billing→Router→Billing
                     → HALTED at hop 6 (handoff pattern repeated) ✅
```

### Tier 3b: Real Web Search Agent
**What it proves:** The guardrail works on **real, unconstrained internet searches**, not just scripted failures.

Uses DuckDuckGo (free, no API key) + Groq for query reformulation.

```
Step 01 | searched 'asdfqwerzxcv...' → NO_RESULTS
Step 02 | LLM reformulated → searched 'python list comprehension' → NO_RESULTS
Step 03-05 | same state → GUARDRAIL FIRED
```

---

## 9. Live Demo Walkthrough

### Demo Step 1 — Open the Chat UI
```
URL: http://127.0.0.1:5050
```

### Demo Step 2 — Prove it's a real AI (not scripted)
Type: `"Hi! What can you do?"`
Type: `"What is a Linear Bounded Automaton?"`
Type: `"1 + 4 ="`

**Point:** This is a real Groq LLM, not a chatbot with hardcoded answers.

### Demo Step 3 — Successful Lookup
Type: `"find product-101"`

**Point:** Agent finds it in 1 step. Guardrail watched but never needed to fire. No loop = no intervention.

### Demo Step 4 — Trigger the Guardrail
Type: `"search for xyz-999"`

Watch the guardrail card appear with:
- Tape filling: `NOT_FOUND → NOT_FOUND → NOT_FOUND → NOT_FOUND`
- Step trace showing each attempt
- Mathematical proof displayed

**Point:** The guardrail did NOT need a timeout or pre-programmed rule about "xyz-999". It detected the loop purely from observing repeated configurations.

### Demo Step 5 — Run the Benchmark
```powershell
python scripts/comparative_benchmark.py
```

Show the table proving LBA_GUARDRAIL outperforms both alternatives.

---

## 10. Conclusion

### What Was Built
A fully functional AI assistant (`GuardMind`) powered by a real cloud LLM (Groq), with a mathematically rigorous safety layer implemented as a Linear Bounded Automaton.

### TOC Concepts Applied

| Concept | Applied Where |
|---|---|
| Finite Automata | The guardrail is a deterministic FSA |
| Linear Bounded Automaton | The bounded tape limits configuration space |
| Pigeonhole Principle | Proves loop detection is complete |
| Decidability Theory | Bounded tape makes halting decidable (vs undecidable for TM) |
| Configuration Analysis | (state, tape) pair fully captures system snapshot |

### Key Results

- ✅ 13 automated tests passing
- ✅ Detects 100% of stuck agent scenarios (3/3 loop periods)
- ✅ Zero false positives on genuine 15-step tasks
- ✅ REPEAT_COUNTER fails on period=3 and period=5 — LBA never does
- ✅ Formula `steps_to_detect = tape_length + period` empirically validated
- ✅ Scales to multi-agent coordination and real internet search

### Future Work
- Extend to concurrent multi-agent systems (Petri net model)
- Sentence embedding for near-duplicate detection (instead of difflib)
- Production deployment with async/streaming responses

---

*Project repository: `lba-agent-guardrail-starter/`*
*Report: `docs/phase3_report.md`*
*Demo: run `chat_server.py` → open `http://localhost:5050`*
