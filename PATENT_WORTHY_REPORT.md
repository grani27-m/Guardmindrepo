# GUARDMIND — Patent-Grade Technical Disclosure
## Deterministic Infinite-Loop Prevention in Autonomous AI Agents Using Linear-Bounded, Finite-Configuration Guardrails

---

| Field | Detail |
|---|---|
| **Invention Title** | GuardMind: Runtime Recurrence Detection Using Bounded Observation History and Exact Configuration Matching in Autonomous AI Agent Execution Loops |
| **Team Member 1** | Rani Gupta — Registration No. 24BIT0543 |
| **Team Member 2** | Swasti Sarangi — Registration No. 24BIT0127 |
| **Institution** | Vellore Institute of Technology, Vellore |
| **School** | School of Computer Science Engineering and Information Systems (SCORE) |
| **Course** | BITE306L — Theory of Computation |
| **Slot** | A2+TA2+TAA2 |
| **Guide** | Dr. Pradeepa M |
| **Academic Year** | 2026–2027 |
| **Disclosure Date** | October 2026 |
| **Technology Readiness Level** | TRL 4 — Validated in Laboratory Environment |

---

> **Note on External Review Integration:**
> An independent external review identified four concerns: (1) prior-art overlap with Microsoft US20260017535A1, (2) configuration-bound formula imprecision (`q × m^n` vs. the correct `q × n × m^n`), (3) overstatement of the term "infinite loop proven", and (4) insufficient differentiation from the AgentLoop (2026) paper.
> **All four concerns are explicitly verified, corrected, and addressed in this report.** A cross-verification table is provided in Appendix A.

---

## SECTION 1 — Title of the Invention

**GuardMind: A Runtime Middleware System for Detecting Repeated Recorded Configurations in Autonomous AI Agent Execution Using a Bounded Observation Tape**

One-line pitch: A lightweight circuit breaker that wraps any AI agent, stores only a fixed-size window of canonical observations, and halts the agent the moment the same (state, tape) configuration recurs — converting a heuristic timeout into a structured, reproducible recurrence check.

---

## SECTION 2 — Field and Area of the Invention

**2.1 Theory of Computation**
Linear Bounded Automata (LBA), formally characterised by Kuroda (1964), are non-deterministic Turing Machines restricted to a tape of length linear in the input. Unlike general Turing Machines — for which the Halting Problem is undecidable (Turing, 1937) — an LBA operates over a strictly finite configuration space bounded by `q × n × m^n`, where `q` is the number of control states, `n` is the tape length, and `m` is the observation alphabet size. GuardMind applies this classical decidability property directly: by bounding an AI agent's observation history to a fixed-length window, it converts the agent's execution trace into an LBA-equivalent model whose configuration space is finite and exhaustible.

**2.2 Autonomous AI Agent Engineering and Runtime Safety**
Modern autonomous agents built on the ReAct framework (Yao et al., 2023) and deployed via LangChain, LangGraph, AutoGPT, and similar frameworks operate through repeated plan–act–observe cycles. When tool calls fail, return empty results, or return rate-limit errors, these agents enter non-terminating execution loops. Research by Hou et al. (2026) identified 68 confirmed infinite-loop failures across 47 projects in a corpus of 6,549 agent repositories — confirming that infinite-loop failures are not edge cases but a systemic class of agent failure. GuardMind provides runtime-level recurrence monitoring that does not require modifying the agent's reasoning logic, prompt structure, or underlying model weights.

**2.3 Cloud and API Cost Optimisation**
Each agent execution step consumes LLM inference tokens, external API quota, and wall-clock time. A non-terminating agent drains these resources silently until a hard step limit is reached. At typical LLM API pricing, a 20-step looping run consuming ~500 tokens per step represents ~10,000 tokens of pure waste per failed invocation — a cost that scales with concurrent agent deployment. GuardMind intervenes at the earliest structurally detectable recurrence of a recorded execution state, consistently reducing wasted steps by 40%–70% in controlled experiments (see Section 8.1).

---

## SECTION 3 — Prior Patents and Publications: Review, Gaps, and Differentiation

### 3.1 Research Papers

| ID | Work | Method | Gap vs. GuardMind |
|---|---|---|---|
| P1 | Hou et al. (2026), arXiv:2607.01641 | Static source-code analysis (IAL-Scan) pre-deployment | No live runtime observation; no bounded-tape recurrence check |
| P2 | Cemri et al. (2025), NeurIPS 2025 | 1,600+ trace annotation; LLM-judge failure taxonomy | Diagnostic only; no runtime halting; no configuration-recurrence check |
| P3 | Xu et al. (2022), NeurIPS 2022 | DITTO training for token-level text repetition | Inside token decoding only; targets output text, not tool-invocation loops |
| P4 | Zheng et al. (2026), arXiv:2609.33315 AgentLoop | Stability signals; continue/synthesise/terminate | Uses task-completion heuristics, NOT bounded-configuration recurrence. Does not apply the Pigeonhole argument over a fixed-length observation tape. GuardMind fires solely when (state, tape) repeats — independent of task-completion judgment. DIFFERENT MECHANISM. |
| P5 | Ibing et al. (2016), IEEE DASC | Branch-target autocorrelation in running binaries | Machine-code level; inapplicable to natural-language tool results |
| P6 | LangChain GRAPH_RECURSION_LIMIT | Fixed step cap on graph execution | Blind to progress vs. repetition; kills legitimate long-running tasks |
| P7 | Geng et al. (2023), EMNLP | CFG/PDA constraints on generated token logits | Targets syntactic output validity, not execution-loop termination |

### 3.2 Patents

| ID | Patent | Gap vs. GuardMind |
|---|---|---|
| T1 | US 6,269,478 B1 — Siemens (2001) | OS-level process monitoring; no semantic observation window; no bounded-tape recurrence |
| T2 | US 10,628,161 B2 — Processor Loop Detection (2020) | Processor-level instruction correlation; not adapted to free-text agent observations |
| T3 | US 12,111,859 B2 — C3.ai (2024) | Agent orchestration; stops when sufficient info available; no exact-match recurrence |
| T4 | WO 2021/084510 A1 — AI Agent Environment (2021) | Agent lifecycle management; no bounded-observation-history recurrence check |

### 3.3 CRITICAL: Differentiation from Microsoft US20260017535A1

> **This is the most important prior-art concern raised by the external review. Fully addressed here.**

**Microsoft US20260017535A1** — "Cyclic Behavior Detection in Generative Agents" — published Jan 15, 2026, priority date July 15, 2024. Claims: monitoring generative-agent responses; configurable window of previous representations; detecting repetition/cyclic behaviour using **semantic embeddings and similarity scores**; triggering mitigation.

**8-Point Precise Technical Differences:**

| Feature | Microsoft US20260017535A1 | GuardMind |
|---|---|---|
| History representation | Embeddings of previous agent responses | Canonical discrete tokens + agent state string in a fixed-length deque |
| Comparison mechanism | Embedding cosine similarity (threshold) | Exact equality of hashable tuple `(state_str, tuple(tape_snapshot))` |
| Configuration key | Embedding vector of response | Compound key: control state AND bounded observation window |
| Detection guarantee | Probabilistic (tunable threshold is a heuristic) | Structural: fires only when identical recorded key found in seen-set |
| Observation canonicalization | Not specified — embeddings on raw responses | Explicit mapping of LLM free text to finite discrete symbol set before tape insertion |
| Response to detection | Mitigation — may reprompt agent to change strategy | Definitive halt — returns HALTED_BY_LBA with specific repeated configuration |
| Multi-agent handling | Included in general scope | Explicit coordination guardrail on handoff-token sequence keyed by task ID |
| Middleware independence | Not disclosed as agent-agnostic | Works with any agent satisfying get_state/act/is_done — model-independent |

**Conclusion:** GuardMind's novel five-element combination — (i) explicit finite-alphabet canonicalization + (ii) compound (state, bounded-tape) configuration key + (iii) exact set-membership recurrence check + (iv) definitive halt with three distinct outcome codes + (v) agent-agnostic middleware interface — does not appear in US20260017535A1.

### 3.4 Research Gaps Identified

1. Step counters and timeouts are representation-blind — fire on elapsed effort, not structural recurrence evidence.
2. Static pre-deployment tools cannot intercept runtime-triggered loops.
3. Processor-level detectors have no semantics for agent observation strings.
4. No agent-agnostic middleware with explicit canonicalization, exact-match recurrence, and structured outcome reporting existed at this disclosure date.
5. AgentLoop (P4) is a fundamentally different class of mechanism — task-completion judgment, not bounded-tape configuration hashing.

---

## SECTION 4 — Summary and Background

### 4.1 Problem

Autonomous AI agents operating in plan–act–observe cycles (Yao et al., 2023) are vulnerable to non-terminating execution when tools fail repeatedly or when delegated sub-goals cannot be resolved. Common real-world failure patterns include:

- **DNS / network resolution failures** triggering indefinite retry cycles on tool endpoints that are temporarily or permanently unavailable.
- **Rate-limited external APIs** returning repeated `429 Too Many Requests` errors that the agent retries without back-off logic.
- **Empty search results** causing a reformulation-and-retry loop where the agent generates new query phrasings but receives the same null response.
- **Multi-agent ping-pong delegation** where two sub-agents — neither able to resolve an ambiguous task — repeatedly hand the task to each other.

Hou et al. (2026) empirically confirmed 68 such failures across 47 open-source agent projects, with a static-analysis precision of 91.9%. Cemri et al. (2025) found that coordination failures accounted for a major share of multi-agent system breakdowns across 1,600+ traced executions. These patterns consume LLM inference tokens, API quota, and cloud compute budget without advancing toward task completion, constituting measurable resource waste at scale.

### 4.2 Why Existing Approaches Fail

- **Hard step limits** cannot distinguish a genuine 50-step research task from a stuck 50-step retry loop.
- **Consecutive-repeat checks** detect only period-1 cycles. An agent cycling A->B->C->A->B->C (period 3) is completely invisible — confirmed experimentally (Section 8).
- **Semantic similarity detectors** (including MS US20260017535A1) introduce false positives and false negatives via threshold miscalibration.

### 4.3 Proposed Solution

GuardMind maintains a fixed-length canonical observation tape, constructs a compound (state, tape) configuration key after each step, and performs O(1) set-membership lookup. Three distinct outcome codes distinguish success, recurrence-based halt, and step-limit exhaustion.

---

## SECTION 5 — Objectives

1. Detect repeated recorded configurations and trigger a structured halt on exact recurrence.
2. Reduce wasted API tokens, tool calls, and LLM inference cost by halting non-progressing execution early.
3. Support any compatible agent through a minimal 3-method interface without modifying agent internals.
4. Make canonicalization explicitly defined — stating when detection is a structural guarantee vs. a recorded-state approximation.
5. Provide tunable sensitivity via tape-length n with documented latency formula n + p under controlled conditions.
6. Deliver a working prototype: 13 passing regression tests, benchmarking scripts, API service layer.

---

## SECTION 6 — Working Principle of the Invention

### 6.1 Step-by-Step Execution Model

The guardrail wraps the agent in a monitoring loop. After each agent step, it updates the bounded tape and performs an O(1) hash-set lookup for configuration recurrence.

```
Step t:
  1. agent.get_state()         -> state_t
     [Returns a canonical state string; must EXCLUDE step counters and timestamps
      to ensure the state can legitimately recur when the agent is stuck.]

  2. agent.act()               -> raw_obs_t
     [Agent invokes a tool or sub-agent. Result may be free-form LLM text.]

  3. canonicalize(raw_obs_t)   -> obs_t
     [Maps raw text to a finite discrete token in Sigma, e.g. NOT_FOUND, TIMEOUT.
      CRITICAL: this is what keeps |Sigma| bounded and enables exact-match detection.]

  4. tape.append(obs_t)        -> tape_t
     [Bounded deque of max length n. Oldest entry auto-discarded when full.]

  5. config_t = (state_t, tuple(tape_t))
     [Compound configuration key — immutable, hashable, O(1) to look up.]

  6. if config_t in seen_configurations:
         -> HALTED_BY_LBA     (recurrence in recorded configuration detected)
     else:
         seen_configurations.add(config_t)
         continue

  7. if agent.is_done(raw_obs_t):
         -> SUCCESS

  (Terminates with: SUCCESS | HALTED_BY_LBA | RAN_OUT_OF_STEPS)
```

### 6.2 Configuration Bound — Corrected Formula

> **Correction of external review finding:** The original docx used the simplified bound |C| <= q * m^n. The implementation in `automaton.py` correctly computes q x n x m^n (the standard LBA bound including tape-head position). This corrected formula is used throughout.

Let:
- Q = set of agent control states; q = |Q|
- Sigma = finite canonical observation alphabet; m = |Sigma|
- n = fixed tape length (configurable, default 4)

|C| <= q x n x m^n

This bound accounts for: q possible agent states; n possible tape-head positions; m^n possible tape contents.

Demo configuration (q=2, m=4, n=4): |C| <= 2 x 4 x 4^4 = 2,048 configurations.

By the Pigeonhole Principle, any run visiting more than 2,048 steps must revisit a configuration — regardless of the agent's internal model weights.

Implementation in automaton.py:
```python
def max_theoretical_configurations(self, num_states: int, alphabet_size: int) -> int:
    n = self.tape.tape_length
    return num_states * n * (alphabet_size ** n)   # q x n x m^n
```

### 6.3 Recorded-State Recurrence vs. Deterministic Loop Proof

> **Correction of external review finding:** The original report used "infinite loop proven." This overstates the guarantee. Corrected language is used throughout.

GuardMind detects **recurrence in the recorded configuration** — not unconditional proof of infinite looping.

**Strong structural guarantee applies when:** The agent's next action depends entirely on the recorded state string and canonical observation window (no hidden model randomness, no external environment state changes). A repeated recorded configuration then implies the same future sequence — a genuine non-terminating cycle.

**Recorded-state approximation (not unconditional proof) when:** The agent has hidden internal state (stochastic temperature, conversational memory outside the tape, external API state changes). GuardMind's halt is then a conservative intervention stopping execution where observable evidence of forward progress is absent.

**Design consequence:** Excluding step counters and timestamps from get_state() is a deliberate design constraint — not just a bug fix — ensuring the recorded state captures only information genuinely relevant to the agent's behaviour.

### 6.4 Canonicalization Layer — Critical LLM Adaptation

**The problem:** LLMs at temperature 0 may return: "Retrying the operation now.", "Retrying operation...", "I'll try the search again." — all semantically equivalent. If raw text entered the tape, every configuration would appear unique, no recurrence would be detected. This is the documented state-leak bug.

**The solution:** The agent's act() method returns a canonical discrete observation token to the guardrail. Raw LLM text is preserved separately for display only.

```python
CANONICAL_SYMBOLS = {
    "FOUND",       # lookup succeeded
    "NOT_FOUND",   # lookup returned empty
    "AUTH_ERROR",  # authentication failure
    "RATE_LIMIT",  # API quota exceeded
    "TIMEOUT",     # tool invocation timed out
    "PARSE_ERROR", # malformed tool response
    "SUCCESS"      # task completed
}
```

The LLM text is shown to users; the canonical token goes into the tape. This keeps |Sigma| bounded, enabling exact-match detection while preserving human-readable outputs.

---

## SECTION 7 — Detailed Description of the Invention

### 7.1 System Architecture (Five Layers)

```
AGENT LAYER
  base_agent.py:     Agent ABC (get_state, act, is_done)
  Implementations:   SolvableTaskAgent, ImpossibleTaskAgent,
                     LLMAgent (Groq/LangChain), InteractiveLookupAgent,
                     RealSearchAgent

GUARDRAIL LAYER
  tape.py:           BoundedTape (collections.deque, maxlen=n)
  config_hasher.py:  make_configuration(state, tape_snapshot)
  automaton.py:      LBAGuardrail (seen-set, halt reason, history)

MIDDLEWARE LAYER
  middleware.py:     run_with_guardrail(agent, guardrail, max_steps)
                     Returns: SUCCESS | HALTED_BY_LBA | RAN_OUT_OF_STEPS

SERVICE LAYER
  api_server.py:     FastAPI POST /guardrail/check
  chat_server.py:    Flask browser UI (port 5050)
  demo_streamlit_app.py

EVALUATION LAYER
  scripts/run_benchmark.py
  scripts/generate_report_charts.py
  report_assets/benchmark_results.csv, comparative_benchmark_results.csv

EXTENSIONS:
  adaptive_guardrail.py       — dynamic tape growth (2 to max 10)
  near_duplicate_guardrail.py — similarity-threshold matching via difflib
  coordination_guardrail.py   — multi-agent handoff sequence monitoring
```

### 7.2 Key Module Implementations

**tape.py — BoundedTape**
```python
class BoundedTape:
    def __init__(self, tape_length: int = 4):
        self._tape = deque(maxlen=tape_length)

    def append(self, observation: str) -> None:
        self._tape.append(str(observation))

    def snapshot(self) -> Tuple[str, ...]:
        return tuple(self._tape)
```

**config_hasher.py**
```python
def make_configuration(state: str, tape_snapshot: Tuple[str, ...]) -> Tuple:
    return (str(state), tuple(tape_snapshot))
```
O(1) hashable lookup. Encodes both control state and bounded observation window.

**automaton.py**
```python
def step(self, state: str, observation: str) -> bool:
    self.tape.append(observation)
    config = make_configuration(state, self.tape.snapshot())
    if config in self.seen_configurations:
        self.halted = True
        self.halt_reason = "Repeated (state, tape) configuration detected."
        return False
    self.seen_configurations.add(config)
    return True
```

**middleware.py**
```python
def run_with_guardrail(agent, guardrail, max_steps=30):
    for _ in range(max_steps):
        state = agent.get_state()
        observation = agent.act()
        if agent.is_done(observation):
            return SUCCESS
        if guardrail is not None and guardrail.step(state, observation) is False:
            return HALTED_BY_LBA
    return RAN_OUT_OF_STEPS
```

### 7.3 Design Decisions Worth Patent-Level Attention

1. **Exclude counters from get_state():** LLMAgent.get_state() returns "goal=X|last=Y" — explicitly excludes self._step. If included, every configuration would be unique, guardrail would never fire. Non-obvious constraint; documented fix for the state-leak bug.

2. **Canonical observations in tape; raw text to display:** Without this decoupling, |Sigma| -> infinity and the configuration bound becomes vacuous.

3. **Three distinct outcome codes:** SUCCESS, HALTED_BY_LBA, RAN_OUT_OF_STEPS allow callers to implement different downstream policies per outcome — not present in step-cap implementations.

### 7.4 Extensions

**Adaptive Tape:** Starts at initial_length=2, grows by growth_step=2 if no detection within patience steps, capped at max_tape_length=10. Always bounded. Key finding: larger tape reduces false positives on legitimate polling; does NOT speed up detection of periodic loops.

**Near-Duplicate Matching:** Replaces exact equality with difflib.SequenceMatcher similarity threshold (default 0.8). Explicitly documented as trading the exact structural guarantee for a tunable approximation.

**Coordination Guardrail:** Applies bounded-tape recurrence to inter-agent handoff token sequences keyed by task ID. Detects multi-agent ping-pong deadlocks invisible to per-agent monitoring.

---

## SECTION 8 — Experimental Validation Results

> All experiments used scripted agents in a controlled laboratory environment. Real-world LLM behaviour may differ. Reported metrics are execution-step counts.

### 8.1 Guarded vs. Unguarded Execution

Source: report_assets/benchmark_results.csv (40 trials, actual recorded data)
Setup: ImpossibleTaskAgent (4-step cycle), max_steps=20, 5 trials per tape length.

| Tape Length n | Unguarded Steps | Guarded Steps | Reduction | Halted by LBA |
|---|---|---|---|---|
| 2 | 20 (always hit cap) | 6 | 70% | 5/5 |
| 4 | 20 (always hit cap) | 8 | 60% | 5/5 |
| 6 | 20 (always hit cap) | 10 | 50% | 5/5 |
| 8 | 20 (always hit cap) | 12 | 40% | 5/5 |

All guarded trials halted at exactly n+4 steps (period p=4). Zero trial-to-trial variance.

### 8.2 Comparison with Alternative Stopping Methods

Source: report_assets/comparative_benchmark_results.csv (actual recorded data)

| Scenario | TIMEOUT (cap=10) | REPEAT_COUNTER | GuardMind (tape=4) |
|---|---|---|---|
| Genuine 15-step task | FAILS — stops at step 10 | Completes at step 15 | Completes at step 15 |
| Stuck, period 1 | Stops at step 10 | Detects at step 2 | Detects at step 5 |
| Stuck, period 3 | Stops at step 10 | NEVER detected (50 steps, FAILED) | Detects at step 7 |
| Stuck, period 5 | Stops at step 10 | NEVER detected (50 steps, FAILED) | Detects at step 9 |

Key findings:
- TIMEOUT: 25% false-positive rate on this test set (kills legitimate work)
- REPEAT_COUNTER: 50% false-negative rate on multi-period loops
- GuardMind: 0% false positives, 0% false negatives — all four scenarios handled correctly

### 8.3 Detection Latency Formula Verification

Empirically confirmed: steps_to_detect = n + p

| Loop Period p | Tape n=2 | Tape n=4 | Tape n=10 |
|---|---|---|---|
| 1 | 3 | 5 | 11 |
| 3 | 5 | 7 | 13 |
| 5 | 7 | 9 | 15 |
| 9 | 11 | 13 | 19 |

All cells equal exactly n+p. Validated across all combinations. Formula holds under constant agent state string and strictly periodic observation cycle.

### 8.4 False-Positive Behaviour on Legitimate Repetition

Setup: Polling agent returning STILL_PROCESSING twice before DONE.

| Tape Length n | Outcome |
|---|---|
| 1 | FALSE HALT at step 2 — healthy agent killed |
| 2 | Completes at step 3 (correct) |
| 3 | Completes at step 3 (correct) |

n=1 produces false positives on legitimate polling. n>=2 correctly handles up to n-1 consecutive identical observations as normal progress.

### 8.5 Near-Duplicate Matching

Setup: Paraphrased retry messages from actual Groq LLM experiments.

| Matching Method | Detection Step |
|---|---|
| Exact matching (core guardrail, raw LLM text) | 12 |
| Similarity threshold 0.90 | 12 |
| Similarity threshold 0.75 | 12 |
| Similarity threshold 0.60 | 5 |
| Similarity threshold 0.45 | 5 |

Canonical matching achieves the same detection as threshold 0.60 — without threshold miscalibration risk.

### 8.6 Multi-Agent Coordination Detection

- Normal billing query: resolved in 2 handoffs (SUCCESS).
- Ambiguous ping-pong task (Router<->Billing<->Router...): coordination guardrail halted at hop 6.

### 8.7 Automated Regression Tests — 13/13 Passing

```
pytest -v: 13 tests, 0 failures, 0 errors

Test Area                | Purpose
-------------------------|----------------------------------------------
Bounded tape             | Retains only last n observations
Configuration snapshots  | Snapshots hashable, usable as dict keys
Repetition detection     | Repeated config triggers halt at correct step
Configuration count      | max_theoretical_configurations = q x n x m^n
Middleware outcomes      | SUCCESS / HALTED_BY_LBA / RAN_OUT_OF_STEPS
```

---

## SECTION 9 — Aspects of the Invention Requiring Patent Protection

The following claims are drafted under the **Indian Patents Act 1970** (as amended through the Patents (Amendment) Act 2005) and **IP India's 2025 Guidelines for Examination of Computer Related Inventions (CRI)**. Under Section 3(k) of the Patents Act, a mathematical method or computer program per se is not patentable. Each claim below is therefore framed as a **computer-implemented method or system** with an explicit **technical effect** that goes beyond the mathematical algorithm itself, establishing industrial applicability and technical contribution.

---

### Claim 1 — Bounded Observation Tape for Agent Execution History

**A computer-implemented method for representing an autonomous software agent's execution history, the method comprising:**
- maintaining, by a processor, a configurable fixed-length observation tape implemented as a bounded queue data structure having a maximum capacity of *n* elements, wherein *n* is a positive integer configurable at system initialization and fixed for the duration of an agent execution run;
- receiving, after each execution step of the agent, a canonical observation symbol selected from a pre-defined finite discrete alphabet Σ, wherein said alphabet is defined prior to agent execution and contains a finite number *m* of distinct symbols representing distinct tool-interaction outcomes;
- appending the received canonical observation symbol to the observation tape and automatically discarding the oldest stored symbol when the tape has reached its maximum capacity *n*;
- producing, upon request, an immutable ordered tuple snapshot of the current tape contents, said snapshot being suitable for use as a component of a hashable configuration key.

**Technical effect:** Converts the agent's potentially unbounded execution history into a finite, bounded representation of size *n* that supports O(1) exact-match set-membership comparison, enabling computationally efficient recurrence detection without full-trace storage.

---

### Claim 2 — Compound Configuration Key and Exact Recurrence Detection

**A computer-implemented method for detecting recurrence in an autonomous agent's execution, the method comprising:**
- constructing, by a processor at each execution step *t*, a compound configuration key *C_t* comprising: (a) a first component being the agent's current control-state string obtained from a `get_state()` call, and (b) a second component being the immutable ordered tuple snapshot of the bounded observation tape as produced by the method of Claim 1;
- maintaining, in memory by a processor, a hash set *S* of previously encountered configuration keys accumulated over the current agent execution run;
- performing, in O(1) time, a set-membership check to determine whether *C_t* is an element of *S*;
- if *C_t* is present in *S*: halting the agent's execution and returning a first outcome constant identifying recurrence-based termination, together with the repeated configuration key *C_t* as evidence;
- if *C_t* is absent from *S*: inserting *C_t* into *S* and permitting the agent to continue execution.

**Technical effect:** Enables deterministic, threshold-free recurrence detection based solely on structural equality of recorded execution state, eliminating the false-positive and false-negative risks inherent in probabilistic similarity-based detection methods.

---

### Claim 3 — Observation Canonicalization for LLM-Backed Agents

**A computer-implemented method for enabling bounded-tape recurrence detection in agents backed by large language models (LLMs), the method comprising:**
- defining, prior to agent execution, a finite canonical observation alphabet Σ consisting of *m* discrete symbolic tokens, each token representing a semantically distinct tool-interaction outcome (for example: `FOUND`, `NOT_FOUND`, `AUTH_ERROR`, `RATE_LIMIT`, `TIMEOUT`, `PARSE_ERROR`, `SUCCESS`);
- receiving, after each agent execution step, a natural-language output string produced by the LLM;
- mapping the received natural-language output string to exactly one member of Σ using a deterministic canonicalization function, thereby keeping the effective alphabet size |Σ| = *m* bounded and independent of the LLM's phrasing variability across runs;
- storing the natural-language output string separately from its canonical token for human-readable display and audit-log purposes;
- supplying only the canonical token, not the natural-language string, as input to the bounded observation tape and configuration key mechanism of Claims 1 and 2.

**Technical effect:** Allows exact-match configuration recurrence detection to function reliably in production LLM-backed agent deployments where raw model outputs vary in phrasing across semantically identical outcomes, resolving the state-leak failure mode in which phrasing variance prevents recurrence from ever being detected.

---

### Claim 4 — Agent-Agnostic Middleware Architecture

**A middleware system for executing an autonomous agent under recurrence-based execution control, the system comprising:**
- an agent interface specification defining a three-method contract: (i) `get_state()` returning a string encoding the agent's current control state, (ii) `act()` returning a canonical observation string post-canonicalization, and (iii) `is_done(observation)` returning a Boolean indicating task completion;
- a guardrail component implementing the bounded observation tape of Claim 1 and the compound configuration key recurrence detection of Claim 2;
- an execution controller that drives the agent through repeated `get_state → act → recurrence-check → is_done` cycles and returns exactly one of three distinct outcome constants upon termination: (a) a first constant indicating successful task completion (`SUCCESS`), (b) a second constant indicating recurrence-based termination (`HALTED_BY_LBA`), and (c) a third constant indicating exhaustion of the configured step limit (`RAN_OUT_OF_STEPS`);
- wherein the execution controller contains no reference to any specific agent implementation, LLM model architecture, external tool, or API provider, making it applicable to any agent satisfying the interface specification.

**Technical effect:** Provides a reusable, composable runtime safety layer that enforces recurrence-based execution control uniformly across arbitrary autonomous agent implementations without requiring modification to the agent's internal logic, prompt engineering, or model weights.

---

### Claim 5 — Configurable Detection Sensitivity via Tape-Length Tuning

**A computer-implemented method for adjusting recurrence detection sensitivity in an autonomous agent execution system, the method comprising:**
- accepting, at system initialization, a positive integer configuration parameter *n* specifying the maximum capacity of the bounded observation tape;
- wherein setting *n* to a smaller value reduces the number of steps required to detect a recurrence for strictly periodic observation cycles (detection latency ≈ *n* + *p* where *p* is the cycle period), at the cost of increased false-positive risk for agents that legitimately produce repeated observations during polling or waiting behaviour;
- wherein setting *n* to a larger value reduces false-positive risk by retaining a longer observation context in each configuration key, at the cost of increased detection latency;
- making the parameter *n* adjustable at runtime initialization without requiring changes to the recurrence detection logic, the hash-set implementation, or any other component.

**Technical effect:** Allows system operators and developers to tune the trade-off between false-positive rate (legitimate agents halted due to incidental observation repetition) and detection latency (execution steps consumed before a stuck agent is halted) without code modification, enabling domain-specific calibration.

---

### Claim 6 — Multi-Agent Handoff Sequence Recurrence Detection

**A computer-implemented method for detecting coordination deadlocks in multi-agent systems, the method comprising:**
- maintaining, by a processor, a bounded sequence of agent-to-agent handoff events occurring within a multi-agent coordination framework, each handoff event comprising a tuple of: (i) an originating agent identifier, (ii) a receiving agent identifier, and (iii) a task identifier;
- applying the compound configuration key construction and exact hash-set recurrence detection mechanism of Claim 2 to the sequence of handoff event tuples, treating each handoff event as an observation in place of an individual agent's tool-call observation;
- halting the multi-agent coordination loop and returning a recurrence-based termination signal when the same handoff configuration key is detected in the set of previously observed handoff configurations.

**Technical effect:** Extends recurrence-based execution control to system-level coordination deadlocks — specifically agent-to-agent ping-pong delegation loops — that are invisible to per-agent monitoring because each individual agent's own observation sequence may not contain a repeated configuration.

---

### Claim 7 — Execution Monitoring with Structured Outcome Reporting

**A computer system for monitoring autonomous agent execution and reporting structured outcomes, the system comprising:**
- a service component configured to receive a task specification, agent configuration, tape-length parameter *n*, and maximum step count;
- an execution controller implementing the middleware architecture of Claim 4;
- a reporting component configured to return, upon execution completion, a structured record comprising:
  - the outcome constant (SUCCESS, HALTED_BY_LBA, or RAN_OUT_OF_STEPS);
  - the total number of execution steps taken;
  - when the outcome is recurrence-based termination: the specific repeated compound configuration key *C_t* that triggered the halt, enabling forensic review;
  - the wall-clock execution time;
- wherein the structured record is sufficient for a downstream monitoring, logging, or alerting system to distinguish recurrence-based termination from ordinary step-limit termination and to implement differentiated remediation actions accordingly.

**Technical effect:** Enables downstream automation pipelines, operational dashboards, and alerting systems to apply distinct remediation logic (e.g., escalate, retry with different parameters, notify operators) for recurrence-based halts versus ordinary step-limit exhaustion, improving operational observability of autonomous agent deployments.

---

## SECTION 10 — Technology Readiness Level (TRL)

| TRL | Description | Status |
|---|---|---|
| 1–2 | Basic principles observed; concept formulated from LBA theory and Turing's decidability framework | ✅ Completed |
| 3 | Analytical and experimental proof of concept; core algorithm validated on mock agents | ✅ Completed |
| **4** | **Technology validated in a laboratory environment with integrated prototype and live LLM testing** | **✅ Current Level** |
| 5 | Technology validated in a relevant environment (production agent framework, real-world tasks) | Not yet achieved |
| 6–9 | Prototype demonstration to full operational deployment | Not yet achieved |

**Why TRL 4 is the correct assessment:**
The core mechanism — bounded observation tape, compound (state, tape) configuration key, exact-match recurrence detection, and agent-agnostic middleware — is fully implemented across 9 Python modules and covered by 13 passing regression tests (0 failures, 0 errors). The implementation has been evaluated in controlled laboratory conditions using both deterministic scripted agents and a live LLM (Groq model `openai/gpt-oss-20b` via LangChain). Operational components include a FastAPI service layer (`api_server.py`), a Flask browser-based chat interface (`chat_server.py`), and a Streamlit demonstration dashboard. Benchmark scripts produce reproducible CSV data and matplotlib charts from real execution runs. Six controlled experiments are documented with actual data (Section 8).

**Why TRL 5 has not yet been achieved:**
The system has not been integrated into a production agent framework (LangGraph, AutoGPT, CrewAI) or evaluated on real-world user-facing tasks at scale. Token consumption and API cost reduction have not been measured in a production deployment. False-positive rates on diverse healthy long-running agents outside the controlled experimental setup remain unmeasured.

**Roadmap to TRL 5:**
1. Integrate GuardMind as a drop-in node guardrail within LangGraph's graph execution model.
2. Evaluate on diverse real-world agent task categories (research, code generation, database retrieval, document Q&A).
3. Measure actual LLM token consumption and API cost reduction in production-scale deployments.
4. Estimate false-positive rates on healthy long-running agents across multiple domains.
5. Conduct concurrency testing for parallel agent execution scenarios.
6. Explore Petri-net modelling as a theoretical extension for genuinely parallel (non-sequential) multi-agent topologies.

---

## SECTION 11 — Threats to Validity and Limitations (Honest Disclosure)

1. Scripted agent experiments: All benchmarks used deterministic scripted agents. Real LLM agents have stochastic elements; detection latency and false-positive rates may differ.
2. Canonicalization dependency: The structural guarantee depends on canonicalization quality. Too-coarse symbol sets conflate distinct failure modes; too-fine sets suffer from phrasing variance.
3. Hidden model state: LLM agents may have hidden internal state (conversation memory, chain-of-thought) not captured in get_state(). A repeated recorded configuration is then a recorded-state approximation, not an unconditional loop proof.
4. Step counter exclusion requirement: get_state() must exclude ever-incrementing counters. This non-obvious constraint must be communicated to developers integrating GuardMind.
5. Tape-length calibration: Tape length must be chosen with knowledge of expected observation patterns. Default n=4 is a general-purpose choice; domain-specific tuning may be required.

---

## SECTION 12 — Master Differentiation Table for Patent Examiner

| Feature | MS US20260017535A1 | AgentLoop (P4, 2026) | GuardMind |
|---|---|---|---|
| History window | Embedding window of responses | Stability signals, recent steps | Fixed-length canonical observation tape |
| Comparison | Cosine similarity (probabilistic) | Task-completion heuristics | Exact equality of compound (state, tape) key |
| Observation alphabet | Unbounded (raw response embeddings) | Unbounded (raw responses) | Explicitly finite, pre-defined |
| Canonicalization | Not specified | Not specified | Explicit, documented, critical design component |
| Outcome on detection | Mitigation (reprompt agent) | Synthesise answer or terminate | Definitive halt — HALTED_BY_LBA |
| Outcome distinctness | Not disclosed | Not disclosed | Three distinct outcome codes |
| Multi-agent | Included in general scope | Not specified | Separate coordination guardrail on handoff sequence |
| Agent interface | Not disclosed as agnostic | Not disclosed | Abstract 3-method interface — any agent, any model |
| Formula | Not stated | Not stated | q x n x m^n — all terms defined |
| False-positive handling | Not disclosed | Not disclosed | Tape-length calibration documented with experiment |

---

## SECTION 13 — References

1. X. Hou, S. Wang, Y. Zhao, H. Wang, "When Agents Do Not Stop: Uncovering Infinite Agentic Loops in LLM Agents," arXiv preprint arXiv:2607.01641, 2026. Available: https://arxiv.org/abs/2607.01641
2. M. Cemri et al., "Why Do Multi-Agent LLM Systems Fail?," Advances in Neural Information Processing Systems (NeurIPS 2025), Datasets and Benchmarks Track, 2025. Available: https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html
3. J. Xu, X. Liu, J. Yan, D. Cai, H. Li, J. Li, "Learning to Break the Loop: Analyzing and Mitigating Repetitions for Neural Text Generation," NeurIPS 2022. Available: https://arxiv.org/abs/2206.02369
4. W. Zheng, M. Xu, K. Hu, J. Ye, C. Xu, "AgentLoop: Runtime Control of Slot-closed Execution Loops for Tool-augmented LLM Agents," arXiv preprint arXiv:2609.33315, 2026. Available: https://arxiv.org/abs/2609.33315
5. A. Ibing, J. Kirsch, L. Panny, "Autocorrelation-Based Detection of Infinite Loops at Runtime," in Proc. IEEE International Conference on Dependable, Autonomic and Secure Computing (DASC), 2016. Available: https://www.sec.in.tum.de/i20/publications/autocorrelation-based-detection-of-infinite-loops-at-runtime
6. LangChain, "GRAPH_RECURSION_LIMIT," LangGraph Documentation. Available: https://langchain-ai.github.io/langgraph/troubleshooting/errors/GRAPH_RECURSION_LIMIT/
7. S. Geng, M. Josifoski, M. Peyrard, R. West, "Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning," in Proc. EMNLP 2023, pp. 10932–10952. Available: https://aclanthology.org/2023.emnlp-main.674/
8. Siemens Aktiengesellschaft, "Monitoring Method for Recognizing Endless Loops and Blocked Processes in a Computer System Using Task State Comparisons," U.S. Patent 6,269,478 B1, issued July 31, 2001. Available: https://patents.justia.com/patent/6269478
9. "Processor for Correlation-Based Infinite Loop Detection," U.S. Patent 10,628,161 B2, issued April 21, 2020. Available: https://patents.google.com/patent/US10628161B2/en
10. C3.ai Inc., "Enterprise Generative Artificial Intelligence Architecture," U.S. Patent 12,111,859 B2, issued October 8, 2024. Available: https://patents.google.com/patent/US12111859B2/en
11. "Executing Artificial Intelligence Agents in an Operating Environment," International Patent Publication WO 2021/084510 A1, published May 6, 2021. Available: https://patents.google.com/patent/WO2021084510A1/en
12. **Microsoft, "Cyclic Behavior Detection in Generative Agents," U.S. Patent Application US20260017535A1, published January 15, 2026, priority date July 15, 2024.** [CRITICAL PRIOR ART — fully addressed in Section 3.3 with 8-point technical differentiation]
13. W. Zhang, Y. Sun, P. Huang, J. Pu, H. Lin, D. Song, "MIRAGE-Bench: LLM Agent is Hallucinating and Where to Find Them," arXiv preprint arXiv:2507.21017, 2025. Available: https://arxiv.org/abs/2507.21017
14. A. M. Turing, "On Computable Numbers, with an Application to the Entscheidungsproblem," Proceedings of the London Mathematical Society, series 2, vol. 42, no. 1, pp. 230–265, 1937. Available: https://doi.org/10.1112/plms/s2-42.1.230
15. S.-Y. Kuroda, "Classes of Languages and Linear-Bounded Automata," Information and Control, vol. 7, no. 2, pp. 207–223, 1964. Available: https://doi.org/10.1016/S0019-9958(64)90120-2
16. S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, Y. Cao, "ReAct: Synergizing Reasoning and Acting in Language Models," International Conference on Learning Representations (ICLR), 2023. Available: https://arxiv.org/abs/2210.03629
17. IP India, "Guidelines for Examination of Computer Related Inventions (CRI)," 2025. Available: https://ipindia.gov.in

---

## APPENDIX A — Cross-Verification of All External Review (ChatGPT) Suggestions

| Suggestion | Verdict | Action Taken |
|---|---|---|
| Microsoft US20260017535A1 is critical overlap that must be addressed | CORRECT AND CRITICAL | Full 8-point differentiation table in Section 3.3 |
| Configuration bound formula should be q x n x m^n, not q x m^n | CORRECT — implementation already uses correct formula | Section 6.2 explicitly states corrected formula with all terms defined |
| "Proven" infinite loop language should be softened | CORRECT — important for patent credibility | Section 6.3 introduces recorded-state recurrence vs. deterministic loop proof distinction |
| AgentLoop (P4) needs explicit differentiation | CORRECT | Section 3.1 P4 entry explicitly states mechanism difference |
| Canonicalization needs precise definition | CORRECT | Section 6.4 defines Sigma, the mapping process, necessity, and consequences |
| Strengthen experimental evidence | PARTIALLY ADDRESSED | Sections 8.1-8.6 include all 6 experiments with actual CSV data cited; production-scale tests remain future work |
| Multi-agent extension should be a separate contribution | CORRECT AND ADOPTED | Claim 6 is independently stated with its own technical effect |
| India Section 3(k) requires technical contribution framing | CORRECT AND CRITICAL | All 7 claims framed as technical methods/systems with explicit technical effects |
| Retain TRL 4, not TRL 3 | CORRECT | TRL 4 adopted in Section 10 with full justification |
| Do not file as broad patent on all AI loop prevention | CORRECT AND ADOPTED | Claims narrowed to specific five-element mechanism combination |
| Recommend focused patentability search before filing | CORRECT | Noted as recommended next step |

---

## APPENDIX B — Key Source Files and Their Role in Patent Claims

| File | Role | Relevant Claim(s) |
|---|---|---|
| `src/lba_guardrail/tape.py` | `BoundedTape` — fixed-length observation window implemented as `collections.deque(maxlen=n)` | Claim 1 |
| `src/lba_guardrail/config_hasher.py` | `make_configuration(state, tape_snapshot)` — compound hashable configuration key | Claim 2 |
| `src/lba_guardrail/automaton.py` | `LBAGuardrail` — seen-set lookup, halt reason, history; `max_theoretical_configurations` = q × n × m^n | Claims 1, 2, 5 |
| `src/lba_guardrail/middleware.py` | `run_with_guardrail` — agent-agnostic executor; returns `SUCCESS / HALTED_BY_LBA / RAN_OUT_OF_STEPS` | Claims 4, 7 |
| `src/lba_guardrail/agents/base_agent.py` | Abstract `Agent` interface (`get_state`, `act`, `is_done`) | Claim 4 |
| `src/lba_guardrail/agents/llm_agent.py` | `LLMAgent` — live Groq/LangChain integration; `get_state()` excludes `self._step` (state-leak fix) | Claims 3, 4 |
| `src/lba_guardrail/agents/interactive_agent.py` | `InteractiveLookupAgent` — canonicalization example: raw LLM text → `FOUND` / `NOT_FOUND` | Claim 3 |
| `src/lba_guardrail/agents/mock_agent.py` | `SolvableTaskAgent`, `ImpossibleTaskAgent` — deterministic scripted agents for testing | Claims 1, 2, 4 |
| `src/lba_guardrail/adaptive_guardrail.py` | `AdaptiveLBAGuardrail` — dynamic tape growth from `initial_length` to `max_tape_length` | Claim 5 |
| `src/lba_guardrail/near_duplicate_guardrail.py` | `NearDuplicateGuardrail` — `difflib.SequenceMatcher` similarity threshold matching | Claim 3 (extension) |
| `src/lba_guardrail/coordination_guardrail.py` | Multi-agent handoff sequence recurrence detection | Claim 6 |
| `src/lba_guardrail/metrics.py` | `RunMetrics` dataclass — steps, halt flag, wall-clock seconds, estimated cost | Claim 7 |
| `api_server.py` | FastAPI `POST /guardrail/check` — service-layer structured outcome reporting | Claim 7 |
| `chat_server.py` | Flask chat UI on port 5050 — browser-based demonstration interface | Claim 7 |
| `report_assets/benchmark_results.csv` | 40 trials of guarded vs. unguarded execution (Section 8.1 data source) | Section 8 |
| `report_assets/comparative_benchmark_results.csv` | Three-method comparison: TIMEOUT vs. REPEAT_COUNTER vs. LBA_GUARDRAIL (Section 8.2 data source) | Section 8 |
| `report_assets/pigeonhole_diagram.png` | Visual proof diagram of the Pigeonhole Principle applied to the bounded configuration space | Section 6 |
| `docs/patent_claims.md` | Draft patent claims (earlier version, superseded by Section 9 of this report) | Section 9 |

---

*End of GuardMind Patent-Grade Technical Disclosure — October 2026*
