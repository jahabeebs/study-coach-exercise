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
  citation IDs. The baseline report
  `eval-report-study-coach-qa-2026-08-10T172259Z.json` therefore contains
  confident answers with fabricated citations and usually no retrieved
  evidence (13/40 assertions across 10 cases).
- Why the unit tests stayed green while evals failed: the grounded test fixture
  replaces the real model with a scripted model that always searches and cites
  its first result. The skip-tools test asserted only response types, so the
  production prompt's behavior was mocked away.
- Fix: require evidence retrieval before course answers, permit world knowledge
  only to reformulate search queries, require exact retrieved citation IDs, and
  retry structured output when its citations violate retrieval provenance. An
  internal `supported` flag lets a searched-but-irrelevant result abstain with
  no citation instead of forcing the model to cite lexical noise.

### Anything else you found

<!-- If you found and addressed anything not listed above, note it here:
     what, how severe, what you did. -->

- The first post-fix run reached 39/40 assertions. The remaining judge failure
  (`eval-report-study-coach-qa-2026-08-10T172808Z.json`) was a genuinely useful
  near-miss: the ENIAC answer added plausible historical implications
  ("marked the beginning" / "drove the next wave") that the
  retrieved section did not state. I tightened the general grounding rule to
  exclude unsupported implications and framing rather than special-casing
  ENIAC.
- The material route joined an arbitrary path and checked only `is_file()`, so
  traversal could read files outside `materials/`. It now resolves the target,
  enforces containment, permits Markdown only, and returns a generic 404;
  direct and percent-encoded traversal regressions cover it.
- The final dependency audit found high-severity advisories in Vite's transitive
  `postcss` and `nanoid` build dependencies. I updated only those lockfile
  entries within the existing ranges; `npm audit` now reports zero
  vulnerabilities and the production build remains green.
- The final post-audit core report,
  `eval-report-study-coach-qa-2026-08-10T182511Z.json`, is 40/40 across 10
  cases with the stricter grouped-fact matcher. This is a fresh stochastic run,
  not a controlled rescore; the saved reports preserve the actual outputs.

## Part 2 — Practice quiz

### Scope decisions

<!-- What you chose where the spec was silent, and why. -->

- A quiz is five questions with four choices, matching the supplied sample and
  the existing `QuizView` contract. A topic resolves to one lesson so a quiz is
  bounded to a coherent evidence set; lesson-level grounding does not guarantee
  every item stays on a narrow subtopic, as the final RAM case shows. Explicit
  `week N` / `lesson N` requests are validated against that lesson; other topics
  strip conversational scaffolding and rank lesson names, headings, and bodies
  as a whole with a winner-confidence gate. Unsupported or ambiguous topics
  return 404 before spending a model request. A final audit caught unrelated
  one-word topics entering through fuzzy body matches; those now require a
  normalized metadata/heading match or an exact raw body term.
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
  leaking between generated quizzes. Leaving during generation aborts the
  browser request and prevents stale UI updates; server-side cancellation and
  request deduplication remain production work.

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
    `eval-report-study-coach-quiz-2026-08-10T174706Z.json` (12/12 under the
    initial contract). Across 15 questions, `correct_index` was never `0`; the
    networks case used only positions `1` and `2`. The first refinement,
    `eval-report-study-coach-quiz-2026-08-10T174948Z.json` (15/15), was a
    false-green: all three quizzes still omitted index `0`, and the plain-text
    judge accepted distractors merely absent from the citation or justified
    from another retrieved chunk.
  - The typed-evidence report,
    `eval-report-study-coach-quiz-2026-08-10T182616Z.json`, covered four topics
    and 20 generated questions. All 16 deterministic assertions passed, while
    the all-or-nothing semantic assertion failed for every quiz (16/20 total).
    It recorded 11 `not_proven` distractors and two quotes absent from the
    item's citation. Actual options included “A LAN uses packet switching,
    while a WAN does not,” “The list must contain no duplicate values,” and
    “The list must have an even number of elements”; their cited excerpts do
    not rule those claims out.
  - I tested two stronger gates and kept their incomplete reports. The private
    author-evidence run
    (`eval-report-study-coach-quiz-2026-08-10T183208Z.json`) returned three
    cases and recorded seven findings (six `not_proven`, one quote mismatch);
    hardware is absent. The request-path-review run
    (`eval-report-study-coach-quiz-2026-08-10T184232Z.json`) contains only two
    of four intended cases and two findings. These fresh stochastic artifacts
    do not record missing-case exceptions, so they cannot prove a controlled
    quality change or why cases are absent; the incomplete coverage itself is
    enough availability risk to reject either gate on a synchronous student
    request. The exact-final-code report,
    `eval-report-study-coach-quiz-2026-08-10T185849Z.json` (16/20), returned all
    four quizzes and passed all 16 deterministic checks. The reviewer failed
    every quiz, recording 14 `not_proven` distractors, two narrow-topic
    relevance failures, and one noncontiguous evidence quote across 9/20 items;
    every indexed answer was still ruled supported. An immediately prior full
    run, `eval-report-study-coach-quiz-2026-08-10T184701Z.json`, also scored
    16/20 but produced different questions/findings. Manual review found most
    flags expose real same-citation gaps, while several also expose judge
    conservatism and inconsistency. I kept the raw red reports instead of
    weakening the rubric or presenting an LLM verdict as ground truth.
- Which evaluator targets which observed failure:

  - `QuizAnswerPositionsVaried` now requires all four indices `{0,1,2,3}` in
    five questions; the production validator applies the same generic rule.
  - `QuizEvidenceJudge` requires five-by-four typed option rulings, exact index
    coverage, a supported indexed answer, contradicted/inapplicable distractors,
    direct requested-topic relevance, and an 8–300-character quote that is
    programmatically found in that item's cited chunk. Each payload pairs a
    public item with only its own cited chunk and excludes private author
    reasoning. One call still contains all five payloads; manual audit caught a
    cross-item inference, so the judge is evidence, not an oracle. The rules
    contain no case-specific answers.
  - The report totals are not a linear trend: case counts and evaluator
    contracts changed. Each JSON artifact preserves its exact generated output,
    retrieved evidence, verdicts, and judge reasons for inspection.

### What I'd do next with more time

- Add a small instructor-reviewed held-out quiz set and calibrate the semantic
  judge against human labels; the refined judge is intentionally stricter, but
  an LLM verdict is still evidence rather than ground truth.
- Move authoring and semantic review off the synchronous student request path,
  let rejected candidates regenerate asynchronously, and grade approved items
  by an immutable server-side quiz ID, as described in the handoff below.

## Part 3 — Senior only

### Failure taxonomy (written BEFORE the fix)

<!-- Clusters you saw in the hard-set failures, the root cause of the
     dominant one, and why you attacked it first. -->

- Baseline: `eval-report-study-coach-hard-2026-08-10T175142Z.json`, 25/36.
  I inspected every answer, citation, retrieved section, and verdict before
  editing the suite.
- Meaningful passes: all 12 `CitationsGrounded` checks. Each citation belonged
  to that run's retrieval evidence, and every answer also cited the expected
  lesson section when checked manually.
- Evaluator false negatives: 11/12 `AnswerMentionsFact` checks. Examples: the
  byte answer says “256 different values,” the ENIAC answer says “1945,” and
  the packet answer says “one kilobyte,” yet each is red. The evaluator searches
  `output.citations` instead of `output.answer`, so it cannot see those facts.
- Evaluator false positive / hollow pass: `glass_tube_replacement` is the only
  green fact check because `transistor` happens to occur in its citation slug.
  The answer itself is correct, but that verdict would stay green even if the
  prose said the opposite.
- Hollow passes: all 12 `AnswerIsSubstantial` checks. `len(answer) > 15` rewards
  long refusals and nonsense and can reject a concise correct answer; it adds no
  trustworthy signal here.
- Genuine agent failure hidden by those checks: the IPv4 answer says every
  internet device has an IPv4 address. The section says every device has an IP
  address and separately distinguishes IPv4 from IPv6. The deterministic fact
  and citation checks cannot see that strengthened quantifier.
- The remaining answers state an accepted fact and cite the expected section;
  `original_text_chars` adds an unnecessary context caveat but still answers
  128 from the cited material. The dominant red cluster was still an evaluator
  defect, so I repaired the measuring instrument before changing the agent.

### The improvement

- Deterministic repair: `AnswerMentionsFact` now inspects normalized answer
  text, not citation strings. Facts are an AND of accepted-phrasing groups;
  numbers use whole-token boundaries, nearby negation invalidates a match, and
  prefix matching must be explicit (`encrypt*`) rather than treating every word
  as a stem. I replaced the length check with `ExpectedSectionCited`. Regression
  tests reject long nonsense, citation-slug-only matches, `165` for `65`,
  negated facts, arbitrary prefixes, and incomplete multi-part answers.
- Controlled comparison:
  `eval-report-study-coach-hard-offline-rescore-2026-08-10T182400Z.json`
  reuses the byte-identical outputs from the 25/36 baseline and applies the
  current three deterministic evaluators/metadata: 36/36, with no model call.
  This isolates the evaluator repair—but the baseline IPv4 overreach also shows
  why 36/36 deterministic assertions are not a complete quality claim.
- A fresh intermediate report,
  `eval-report-study-coach-hard-2026-08-10T175523Z.json`, also scored 36/36 but
  made two unsupported additions: transistors packed "by the millions" where
  the section says "many," and every device having IPv4. That hollow green led
  me to add the course-evidence faithfulness judge and tighten the agent's
  generic scope/quantifier rules rather than special-case either question.
- Final fresh report:
  `eval-report-study-coach-hard-2026-08-10T182707Z.json`, 48/48 (12 cases × four
  assertions, including faithfulness). I inspected all raw outputs; the glass-
  tube and IPv4 answers avoid the earlier overreach.
- Why this should generalize: the matchers operate on metadata fact groups and
  normalized answer text, provenance uses per-run retrieval, and the judge sees
  retrieved chunks rather than case-specific expected prose. The offline 36/36
  and fresh 48/48 use different assertion sets; they are separate evidence, not
  a linear score improvement, and fresh generations remain stochastic samples.

### Handoff note (ADR-style, ~half a page)

<!-- The pod rotates off; the course team's engineers run this for ~10k
     students. What changes first? What must they know? -->

**Decision: replace per-request quiz generation with versioned, reviewed quiz
authoring before scaling to 10k students.** The prototype makes a synchronous
model call for every quiz and sends the answer key to the browser. That is a
reasonable local formative-learning tradeoff, but at course scale it creates
variable latency/cost, model-drift risk, inconsistent student experiences, and
no academic-integrity boundary.

The first production slice should generate candidate questions against an
immutable course-material version, record the prompt/model/material hashes and
retrieved evidence, run the deterministic and semantic validators, and put the
result in an instructor approval queue. Approved questions become cached,
immutable quiz IDs. Students receive a sampled quiz without `correct_index`;
submissions are graded server-side against that ID. This trades per-request
novelty for trust, predictable cost, reproducibility, and operability—the right
trade for instruction at this scale.

Next, add institutional authentication/authorization, rate limits and quotas,
attempt persistence, audit logs, latency/token/error telemetry, accessibility
automation plus manual checks, and retention/privacy rules. Treat evaluator
scores as monitored evidence, not truth: maintain a versioned, instructor-
reviewed held-out set, calibrate the LLM judge against human labels, inspect raw
outputs on regressions, and pin model/prompt changes through that release gate.
The current API is intended and documented for localhost use; it is not
hardened against external exposure until those controls exist.
