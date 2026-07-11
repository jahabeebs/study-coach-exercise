# Tasks

Start the clock with your first commit. Budgets are guidance, not gates —
but when time is up, stop and write down what's left in SOLUTION.md.

**Mid-level track:** Parts 1 and 2 (90 min).
**Senior track:** Parts 1, 2, and 3 (120 min).

---

## Part 1 — Make it trustworthy (~25 min)

The team knows something is off. Two signals are waiting for you:

1. `make test` — the suite is not green.
2. `make evals` — run it and read the report (needs your API key).

Find and fix the defects behind **both** signals. In SOLUTION.md, explain each
root cause and — for the second one — why the unit tests stayed green while
the evals failed. Fix causes, not symptoms: if your fix makes another test
fail, that test is telling you something.

## Part 2 — The practice-quiz feature, evals first (~50–60 min)

From the Product Owner on your pod:

> *Students keep asking for a way to test themselves before the weekly quiz.
> Could Study Coach generate a short practice quiz on a topic the student
> picks, and tell them how they did? It has to stick to what's actually in
> the course materials — instructors will lose trust the moment a question
> comes from outside the course. There's a sample of the quiz format in the
> materials folder. The web page already has a "Practice quiz" tab that goes
> nowhere; the last engineer left a `QuizView` component ready.*

That's the whole spec — like real pod work, it's underspecified on purpose.
Make sensible scope calls and record them (and the questions you'd ask the
PO) in SOLUTION.md.

Requirements:

- **Evals first (or alongside):** add eval cases for quiz generation with at
  least one **programmatic** evaluator and one **LLM-judge** criterion.
  Then — this is required — run your feature against your cases, paste 2–3
  observed failures (or near-misses) into SOLUTION.md, and make sure at least
  one evaluator targets something you actually observed. Commit the reports.
- **Backend:** a quiz-generation endpoint, grounded in the course materials
  with the same citation discipline as chat.
- **Frontend:** wire the "Practice quiz" tab end to end using the provided
  `QuizView` component (its header comment documents the props contract —
  treat it as the spec; you shouldn't need to modify it).
- **Stretch goal (only if time remains — skipping it is a valid scope call):**
  grading with per-question feedback.

## Part 3 — Senior only: the scorecard is lying (~25 min)

The previous engineer left a second eval suite of harder, casually-phrased
questions, with its own evaluators in `evals/hard_evaluators.py`. Run it:

```bash
cd backend && uv run python ../evals/run_evals.py --suite hard
```

Read the scorecard skeptically. **An eval suite is itself a thing under test:
a green check can be hollow and a red X can be the evaluator's fault, not the
agent's.** Your job:

1. **Error analysis.** Actually look at the outputs (not just the pass/fail
   column). In SOLUTION.md, classify what you see: which reported results
   reflect the agent's real behavior, which are the *evaluators* misjudging a
   correct (or incorrect) answer, and which "passes" are meaningless. Do this
   before changing anything.
2. **Fix the evaluation** so the scorecard tells the truth. At minimum, repair
   the evaluator(s) that are giving wrong verdicts; strengthen or replace any
   that measure nothing.
3. **Then** fix the *agent* only where a failure is genuinely the agent's
   fault — which may be nowhere, and saying so (with evidence) is a fine
   answer.
4. Commit before/after eval reports.

A hidden held-out set of fresh questions is run against your final commit, so
evaluator fixes that generalize beat ones that special-case these twelve.
We're looking for the instinct to trust data over a dashboard — a correct
diagnosis beats a big green number.

Finally, add a short **handoff note** (ADR-style, ~half a page, in
SOLUTION.md): the pod rotates off next month and the course team's own
engineers take this over for ~10k students. What would you change first, and
what should they know?
