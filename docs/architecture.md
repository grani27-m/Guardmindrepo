# Architecture (written explanation)

The architecture is intentionally simple and modular. At the outermost layer sits the agent, which produces a current state and an observation after each action. The guardrail sits directly between the agent and the execution loop. It stores the agent's recent observations in a bounded tape and computes a finite configuration key from the concatenation of the state and tape snapshot.

The middleware then checks whether that configuration has appeared before. If a repeated configuration appears, the middleware halts the loop immediately and returns a signal such as `HALTED_BY_LBA`. This is the critical mechanism: the system does not guess based on elapsed time or the number of tool calls; it proves the loop by repeated configuration detection.

The tape must be bounded because the finite-memory assumption is what reduces an otherwise unbounded execution trace into a finite number of possible system states. In terms of the formal model, if the tape length is fixed at `n`, the number of possible configurations is bounded by `q × n × m^n`, where `q` is the number of control states and `m` is the alphabet size. With a bounded tape, the system is effectively an LBA, and repeated state plus tape content is a formal proof of non-termination.

A worked example:
- tape length = 4
- state remains `state=retry_loop`
- observation cycle = `[ERROR: DNS_RESOLUTION_FAILED, RETRY: GOOGLE_SEARCH_NO_RESULTS, RETRY: SCRAPER_TIMEOUT, RETRY: GOOGLE_SEARCH_NO_RESULTS]`
- after a few rounds, the same state and the same recent tape pattern reappear
- at that point the guardrail returns `False`, which marks the loop as proven and stops the process

This same idea works for both a mock agent and a real LLM-backed agent, because the middleware only requires a minimal `Agent` interface: `get_state()`, `act()`, and `is_done()`.

A simple diagram for the report is:
Agent -> [state, observation] -> LBAGuardrail -> continue or HALT -> middleware response

This is the architecture used by the API and benchmark pipeline as well.
