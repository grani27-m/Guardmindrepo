"""
Near-Duplicate Configuration Matching

The problem this solves: earlier in this project, real Groq responses like
"Retrying the operation now." and "Retrying operation..." are semantically
identical but NOT string-identical. An exact-match guardrail either misses
the loop entirely, or (as we saw) takes much longer to detect it than
necessary, because it's effectively waiting for the LLM to coincidentally
produce byte-identical text twice.

This version replaces exact equality with a similarity THRESHOLD using
Python's built-in difflib (zero external dependencies, fully offline,
fully explainable -- no black-box embedding model to defend to a
professor). For a production system you'd likely use sentence embeddings
instead (see the note at the bottom for how to swap that in using your
own Groq key + a local embedding model).

IMPORTANT theoretical honesty for your report: switching from exact
match to similarity-threshold match trades a hard mathematical guarantee
(exact configuration repetition is unambiguous) for a tunable heuristic
(similarity above threshold X is "close enough"). State this trade-off
explicitly -- it's the difference between "provably decidable" and
"decidable up to a chosen approximation," which is still a legitimate,
useful engineering design, but a different (weaker) formal claim than
your core exact-match guardrail. Present both: the exact-match version
as your primary, provable claim, and this as an optional, practical
extension for noisy real-world text.
"""

import difflib
from collections import deque
from typing import Tuple, Optional, List


class NearDuplicateGuardrail:
    def __init__(self, tape_length: int = 4, similarity_threshold: float = 0.8):
        self.tape_length = tape_length
        self.threshold = similarity_threshold
        self.tape: deque = deque(maxlen=tape_length)
        # Unlike the exact-match version, we can't use a set() of hashable
        # tuples, because similarity isn't a hash-based equality. We keep
        # a list of (state, tape_snapshot) pairs seen so far and compare
        # against all of them -- O(k) per step, fine for a course project
        # and small k; a production system would use approximate nearest
        # neighbor search (e.g. FAISS) for scale.
        self.seen: List[Tuple[str, Tuple[str, ...]]] = []
        self.halted = False
        self.halt_reason: Optional[str] = None

    def _tape_similarity(self, tape_a: Tuple[str, ...], tape_b: Tuple[str, ...]) -> float:
        if len(tape_a) != len(tape_b):
            return 0.0
        if len(tape_a) == 0:
            return 1.0
        scores = [
            difflib.SequenceMatcher(None, a, b).ratio()
            for a, b in zip(tape_a, tape_b)
        ]
        return sum(scores) / len(scores)

    def step(self, state: str, observation: str) -> bool:
        if self.halted:
            return False

        self.tape.append(observation)
        current_tape = tuple(self.tape)

        for (seen_state, seen_tape) in self.seen:
            if seen_state != state:
                continue
            sim = self._tape_similarity(current_tape, seen_tape)
            if sim >= self.threshold:
                self.halted = True
                self.halt_reason = (
                    f"Near-duplicate configuration found (similarity={sim:.2f} "
                    f">= threshold={self.threshold}): current={current_tape} "
                    f"~ previous={seen_tape}"
                )
                return False

        self.seen.append((state, current_tape))
        return True


# ---------------------------------------------------------------------
# Demonstration: replaying the EXACT phrasing variance we saw from
# real Groq output earlier in this project
# ---------------------------------------------------------------------

REAL_GROQ_VARIANTS = [
    "Retrying the operation now.",
    "Retrying operation...",
    "Retrying the operation now.",
    "Hmm, that wasn't found. Retrying the lookup now.",
    "Retrying operation...",
    "No match in the database. Trying again.",
    "Retrying operation...",
    "Lookup failed. Attempting a retry.",
]


def run_exact_match(observations, state="stuck_task", tape_length=4, max_steps=20):
    tape = deque(maxlen=tape_length)
    seen = set()
    for i, obs in enumerate(observations[:max_steps], start=1):
        tape.append(obs)
        config = (state, tuple(tape))
        if config in seen:
            return "HALT", i
        seen.add(config)
    return "NO_HALT_WITHIN_BUDGET", len(observations[:max_steps])


def run_near_duplicate(observations, state="stuck_task", tape_length=4,
                        threshold=0.6, max_steps=20):
    g = NearDuplicateGuardrail(tape_length=tape_length, similarity_threshold=threshold)
    for i, obs in enumerate(observations[:max_steps], start=1):
        can_continue = g.step(state, obs)
        if not can_continue:
            return "HALT", i, g.halt_reason
    return "NO_HALT_WITHIN_BUDGET", len(observations[:max_steps]), None


if __name__ == "__main__":
    # Cycle the real variant phrases to simulate a longer real run
    long_run = (REAL_GROQ_VARIANTS * 3)[:20]

    print("Replaying REAL Groq phrasing variance captured earlier in this project.")
    print("Observations (first 8):")
    for o in long_run[:8]:
        print(f"  - {o!r}")

    print("\n--- EXACT MATCH (your current guardrail) ---")
    result, steps = run_exact_match(long_run, tape_length=4)
    print(f"Result: {result} at step {steps}")

    print("\n--- NEAR-DUPLICATE MATCH (similarity >= 0.6) ---")
    result, steps, reason = run_near_duplicate(long_run, tape_length=4, threshold=0.6)
    print(f"Result: {result} at step {steps}")
    if reason:
        print(f"Reason: {reason}")

    print("\nInterpretation for your report:")
    print("Exact match either takes longer to fire (waiting for byte-identical")
    print("text) or, in the worst case, never fires within a practical step")
    print("budget if the LLM keeps phrasing things slightly differently.")
    print("Near-duplicate match correctly recognizes that 'Retrying the")
    print("operation now.' and 'Retrying operation...' represent the SAME")
    print("underlying stuck state, and halts sooner -- at real cost savings,")
    print("but with a weaker (approximate, threshold-tuned) formal guarantee")
    print("than exact match. State this trade-off explicitly in your report.")

    print("\n--- Sensitivity: does the threshold matter? ---")
    for thresh in [0.9, 0.75, 0.6, 0.45]:
        result, steps, _ = run_near_duplicate(long_run, tape_length=4, threshold=thresh)
        print(f"  threshold={thresh}: {result} at step {steps}")
