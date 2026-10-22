# Draft Patent Claims

These are draft claims for the Phase 3 report. They are written for the purposes of technical patent drafting and should be refined with a professor or advisor.

1. **Bounded-memory execution mapping:** A method for representing an autonomous software agent's execution history as a finite tape structure having a configurable maximum length, such that the agent's recent state and observation history is mapped into a bounded memory representation suitable for linear-bounded automaton analysis.

2. **Configuration-repetition halting proof:** A method for proving that an autonomous agent has entered an infinite execution loop by detecting the repetition of a combined configuration consisting of the agent's current state and the bounded tape snapshot, where the repeated configuration establishes a non-terminating cycle without relying on a heuristic timeout.

3. **Agent-agnostic middleware architecture:** A middleware system configured to wrap any agent implementation satisfying a minimal state-action-completion interface and to automatically enforce loop detection and safe termination based on the repeated configuration proof.

4. **Configurable detection sensitivity:** A method of adjusting the bounded tape length to tune loop-detection sensitivity and latency, thereby balancing memory usage against the time to identify a repeated execution cycle.

5. **Cost-aware execution control:** A system for terminating an autonomous agent before it consumes unbounded AI API or compute resources, thereby reducing wasted tokens, tool calls, or cloud execution cost while preserving otherwise normal task execution for terminating runs.
