# SOLUTION.md

Keep it tight — bullets over prose. This document is weighted heavily in
review: it's how we see your judgment, not just your code.

## Video links

Both videos are required. Paste their links here (any host — Loom, Drive,
unlisted YouTube), or write "sent by email" and email the files with your
submission reply. Don't commit large video files into the repo.

- Walkthrough (Video 1):
- AI workflow (Video 2):

## Part 1 — Bugs

### Bug caught by the tests

- Root cause: `search()` sorted BM25-style scores in ascending order, then
  returned the first `k`, so callers received the weakest matches first.
- Fix (and why this is the cause, not a symptom): sort scores descending to
  restore the documented best-first contract.
- Anything else the fix forced you to change, and why: `best_section()` had
  compensated for the defect by taking the last result. It must take the first
  result once the shared ordering contract is fixed.

### Bug caught by the evals

- Root cause: the production prompt explicitly told the model to answer from
  its own knowledge, avoid retrieval unless asked, and emit merely plausible
  citation IDs. The baseline report therefore contains confident answers with
  fabricated citations and usually no retrieved evidence (13/40 assertions).
- Why the unit tests stayed green while evals failed: the grounded test fixture
  replaces the real model with a scripted model that always searches and cites
  its first result. The skip-tools test asserted only response types, so the
  production prompt's behavior was mocked away.
- Fix: require evidence retrieval before course answers, permit world knowledge
  only to reformulate search queries, require exact retrieved citation IDs, and
  retry structured output when its citations violate retrieval provenance.

### Anything else you found

<!-- If you found and addressed anything not listed above, note it here:
     what, how severe, what you did. -->

- The first post-fix run reached 39/40 assertions. The remaining judge failure
  was a genuinely useful near-miss: the ENIAC answer added plausible historical
  implications ("marked the beginning" / "drove the next wave") that the
  retrieved section did not state. I tightened the general grounding rule to
  exclude unsupported implications and framing rather than special-casing
  ENIAC.

## Part 2 — Practice quiz

### Scope decisions

<!-- What you chose where the spec was silent, and why. -->

- A quiz is five questions with four choices, matching the supplied sample and
  the existing `QuizView` contract. A topic resolves to one lesson so a quiz is
  coherent; explicit `week N` / `lesson N` requests are deterministic, while
  other topics use best-first retrieval. Unsupported topics return 404 before
  spending a model request.
- Retrieval is application-owned: the model receives all six sections from the
  selected lesson, but it can cite only those exact IDs. The response retains
  the retrieved IDs/chunks so both deterministic evaluators and the judge can
  audit provenance.
- I included the stretch grading path because the core slices were healthy at
  the scope gate. For this single-user localhost prototype, the browser retains
  `correct_index` and grades locally; the UI labels the result as an unsaved
  self-check. This is deliberately not an academic-integrity boundary.
- Quiz state is intentionally ephemeral. Starting a new quiz or leaving the tab
  resets answers and results; a fresh React key prevents selection state from
  leaking between generated quizzes.

### Questions I'd ask the Product Owner

- Does “topic” mean any phrase a student types, or should the product constrain
  selection to a module/lesson taxonomy with guaranteed coverage?
- Is practice grading only formative, or must answers be tamper-resistant and
  auditable? The latter requires server-side grading and changes the API shape.
- Should generated quizzes be reproducible/shareable for instructors, and do
  students need attempts, progress, accommodations, or persistence?

### Evals

- Observed failures/near-misses from running my feature (2–3 examples, paste
  the actual outputs):

  - Initial report:
    `eval-report-study-coach-quiz-2026-08-10T174706Z.json` (12/12). The green
    score still hid placement bias: across 15 questions, `correct_index` was
    never `0`; the networks case used only positions `1` and `2`.
  - Hardware near-miss: a GPU distractor claimed GPUs have “a higher clock
    speed measured in gigahertz than any CPU.” The cited section supports the
    parallel-core answer but does not let a student rule out that absolute
    distractor. The judge passed it because it was merely absent from the text.
  - Networks near-miss: the router question offered “To reassemble out-of-order
    packets into the original file.” Its cited routing section does not say who
    reassembles packets; the judge had to borrow that fact from a different
    retrieved section. The item remained answerable, but its own citation was
    not sufficient to eliminate every distractor.
- Which evaluator targets which observed failure:

  - `QuizAnswerPositionsVaried` requires at least three distinct correct-answer
    positions in five questions; the production validator applies the same
    generic property and retries instead of teaching students a position cue.
  - The refined LLM judge requires the indexed answer to be supported *and*
    each distractor to be clearly wrong or inapplicable from that question's
    cited chunk. The quiz prompt carries the same rule; it does not contain any
    topic, case name, or visible answer.

### What I'd do next with more time

## Part 3 — Senior only

### Failure taxonomy (written BEFORE the fix)

<!-- Clusters you saw in the hard-set failures, the root cause of the
     dominant one, and why you attacked it first. -->

### The improvement

- What and why:
- Before/after (report files):
- Why this should generalize beyond the visible cases:

### Handoff note (ADR-style, ~half a page)

<!-- The pod rotates off; the course team's engineers run this for ~10k
     students. What changes first? What must they know? -->
