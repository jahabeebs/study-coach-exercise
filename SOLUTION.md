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

- **Root cause:** `search()` sorted BM25-style scores in ascending order and
  returned the first `k`, giving callers the weakest matches first.
- **Fix (and why this is the cause rather than a symptom):** Sort scores in descending
  order to restore the documented best-first contract.
- **Anything else the fix forced you to change, and why:** `best_section()`
  compensated for the bug by taking the last result. Once the shared ordering
  contract is fixed, it must take the first result.

### Bug caught by the evals

- **Root cause:** The production prompt told the model to answer from its own
  knowledge, skip retrieval unless asked, and emit citation IDs that only
  needed to look plausible. The baseline report,
  `eval-report-study-coach-qa-2026-08-10T172259Z.json`, contains confident
  answers with fabricated citations and usually no retrieved evidence: 13/40
  assertions passed across 10 cases.
- **Why the unit tests stayed green while evals failed:** The grounded test
  fixture replaces the real model with a scripted model that always searches
  and cites its first result. The skip-tools test checked only response types.
  Neither test exercised the production prompt's behavior.
- **Fix:** Require evidence retrieval before answering course questions. World
  knowledge may only reformulate search queries, and citations must exactly
  match retrieved IDs. Structured output is retried when its citations violate
  retrieval provenance. An internal `supported` flag allows a search with no
  relevant result to abstain without a citation, so the model does not have to
  cite lexical noise.

### Anything else you found

<!-- If you found and addressed anything not listed above, note it here:
     what, how severe, what you did. -->

- The first post-fix run reached 39/40 assertions. In the remaining judge
  failure, `eval-report-study-coach-qa-2026-08-10T172808Z.json`, the ENIAC
  answer added plausible historical implications ("marked the beginning" /
  "drove the next wave") that its retrieved section did not state. I tightened
  the general grounding rule to exclude unsupported implications and framing.
  I did not add an ENIAC-specific rule.
- The material route joined an arbitrary path and checked only `is_file()`,
  allowing path traversal to read files outside `materials/`. It now resolves
  the target, enforces containment, allows only Markdown, and returns a generic
  404. Regression tests cover direct and percent-encoded traversal.
- The final dependency audit found high-severity advisories in Vite's transitive
  `postcss` and `nanoid` build dependencies. I updated only those lockfile
  entries within the existing ranges; `npm audit` now reports zero
  vulnerabilities and the production build remains green.
- The final post-audit core report,
  `eval-report-study-coach-qa-2026-08-10T182511Z.json`, scored 40/40 across 10
  cases with the stricter grouped-fact matcher. It is a fresh stochastic run,
  not a controlled rescore. The saved reports preserve the actual outputs.

## Part 2 — Practice quiz

### Scope decisions

<!-- What you chose where the spec was silent, and why. -->

- Each quiz has five questions and four choices per question, matching the
  supplied sample and the existing `QuizView` contract. A topic resolves to one
  lesson, which keeps the evidence set coherent. That lesson-level grounding
  does not guarantee that every item will stay on a narrow subtopic; the final
  RAM case shows this limitation. Explicit `week N` and `lesson N` requests are
  validated against that lesson. For other topics, the application removes
  conversational scaffolding, ranks lesson names, headings, and bodies
  together, and applies a winner-confidence gate. Unsupported or ambiguous
  topics return 404 before using a model request. A final audit found that fuzzy
  body matches admitted unrelated one-word topics. Those topics now need either
  a normalized metadata or heading match, or an exact raw body term.
- The application owns retrieval. The model receives all six sections from the
  selected lesson and may cite only those exact IDs. The response retains the
  retrieved IDs and chunks so the deterministic evaluators and the judge can
  audit provenance.
- Quiz authoring and semantic review are separate model responsibilities. The
  author produces the five-question draft; then five isolated review calls run
  concurrently at temperature zero. Each reviewer sees one public question
  and only that question's cited chunk. It verifies topic relevance, exact
  option coverage, an evidence-supported indexed answer, the absence of a
  second supported option, and quote provenance. A `not_proven` distractor is
  recorded as weaker evidence, but it is still acceptable when the cited
  material supports only one defensible answer.
- When review rejects an item, the application preserves accepted questions
  and repairs only the failed item. It generates three generic repair variants
  concurrently, requires a structured option-level evidence plan, and sends
  each candidate through the independent reviewer. The application, rather
  than the model, preserves the original citation and required answer position;
  it deterministically repositions a repair's correct option before review when
  necessary. Two bounded repair rounds are allowed before the API fails safely
  with 502 instead of returning a quiz that did not pass review.
- I added the stretch grading path after the core slices passed the scope gate.
  In this single-user localhost prototype, the browser retains `correct_index`
  and grades locally. The UI describes the result as an unsaved self-check. It
  does not provide an academic-integrity boundary.
- Quiz state is ephemeral. Starting a new quiz or leaving the tab clears the
  answers and results. A fresh React key prevents selection state from leaking
  between generated quizzes. Leaving during generation aborts the browser
  request and blocks stale UI updates. Server-side cancellation and request
  deduplication remain production work.

### Questions I'd ask the Product Owner

- Does “topic” mean any phrase a student types, or should the product constrain
  selection to a module/lesson taxonomy with guaranteed coverage?
- Is practice grading only formative, or must answers be tamper-resistant and
  auditable? The latter requires server-side grading and changes the API shape.
- Should generated quizzes be reproducible/shareable for instructors, and do
  students need attempts, progress, accommodations, or persistence?

### Evals

- **Observed failures/near-misses from running my feature (2–3 examples, paste
  the actual outputs):**

  - The initial report,
    `eval-report-study-coach-quiz-2026-08-10T174706Z.json`, scored 12/12 under
    the initial contract. Across 15 questions, `correct_index` was never `0`;
    the networks case used only positions `1` and `2`. The first refinement,
    `eval-report-study-coach-quiz-2026-08-10T174948Z.json`, scored 15/15 but was
    a false green. All three quizzes still omitted index `0`, and the plain-text
    judge accepted distractors when the citation did not mention them or when a
    different retrieved chunk justified them.
  - The typed-evidence report,
    `eval-report-study-coach-quiz-2026-08-10T182616Z.json`, covered four topics
    and 20 generated questions. All 16 deterministic assertions passed, while
    the all-or-nothing semantic assertion failed for every quiz (16/20 total).
    It recorded 11 `not_proven` distractors and two quotes absent from the
    item's citation. Actual options included “A LAN uses packet switching,
    while a WAN does not,” “The list must contain no duplicate values,” and
    “The list must have an even number of elements”; their cited excerpts do
    not rule those claims out.
  - I tested stronger gates and kept their incomplete reports. The private
    author-evidence run,
    `eval-report-study-coach-quiz-2026-08-10T183208Z.json`, returned three cases
    and recorded seven findings: six `not_proven` rulings and one quote
    mismatch. The hardware case is absent. The request-path-review run,
    `eval-report-study-coach-quiz-2026-08-10T184232Z.json`, contains only two of
    four intended cases and two findings. These fresh stochastic artifacts do
    not record missing-case exceptions. They cannot show a controlled quality
    change or explain why cases are absent. A whole-quiz review-and-retry design
    then returned only two cases in
    `eval-report-study-coach-quiz-2026-08-10T193222Z.json`: one weak question
    forced regeneration of all five, making retry granularity an availability
    problem. That led to isolated per-question review and targeted repair,
    which preserves accepted work and bounds the failure surface.
  - The targeted-repair reports preserve the remaining iterations rather than
    presenting a monotonic score story. They exposed a contract mismatch where
    a repair author could identify the right answer at a different option index
    from the position owned by the application. The application now performs a
    deterministic swap into the required position before independent review.
    The final report,
    `eval-report-study-coach-quiz-2026-08-10T195414Z.json`, returned all four
    configured topics and scored 20/20: 16 deterministic assertions and four
    semantic-review assertions. Every accepted item had an evidence-supported
    indexed answer, no second supported option, direct topic relevance, and
    reviewer quotes found in its cited chunk. The 139-test backend suite also
    covers review isolation, bounded retries, targeted repair, position
    preservation, quote provenance, unsupported topics, and safe failure. This
    is one stochastic sample, so I retained the intermediate and red reports
    rather than treating 20/20 as proof of ground truth.

- **Which evaluator targets which observed failure:**

  - `QuizAnswerPositionsVaried` now requires all four indices `{0,1,2,3}` in
    five questions; the production validator applies the same generic rule.
  - `QuizEvidenceJudge` reviews each question in an isolated call. It requires
    exact question and option-index coverage, a supported indexed answer, no
    supported distractor, direct relevance to the requested topic, and an
    8–300-character quote that is programmatically found in that item's cited
    chunk. `contradicted` and `inapplicable` are stronger distractor evidence;
    `not_proven` is accepted as a weaker but still evidence-bounded wrong option
    when the chunk supports exactly one answer. Production and evals share the
    same typed review models, instructions, and validation function. The
    reviewer never receives sibling questions, sibling chunks, or private
    author reasoning, preventing cross-item inference. The rules contain no
    case-specific answers, and the model verdict remains fallible evidence.
  - The report totals do not form a linear trend because case counts and
    evaluator contracts changed. Each JSON artifact preserves its exact
    generated output, retrieved evidence, verdicts, and judge reasons for
    inspection.

### What I'd do next with more time

- Add a small instructor-reviewed held-out quiz set and calibrate the semantic
  judge against human labels. The refined judge is stricter. Its verdicts are
  supporting evidence and cannot establish ground truth.
- Move the current multi-call author, per-item review, and targeted-repair
  pipeline off the synchronous student request path. Author and approve items
  asynchronously, then grade approved items by an immutable server-side quiz
  ID, as described in the handoff below.

## Part 3 — Senior only

### Failure taxonomy (written BEFORE the fix)

<!-- Clusters you saw in the hard-set failures, the root cause of the
     dominant one, and why you attacked it first. -->

- Baseline: `eval-report-study-coach-hard-2026-08-10T175142Z.json` scored 25/36.
  Before editing the suite, I inspected every answer, citation, retrieved
  section, and verdict.
- All 12 `CitationsGrounded` checks were meaningful passes. Each citation
  belonged to that run's retrieval evidence, and manual review confirmed that
  every answer also cited the expected lesson section.
- 11/12 `AnswerMentionsFact` checks were evaluator false negatives.
  For example, the byte answer says “256 different values,” the ENIAC answer
  says “1945,” and the packet answer says “one kilobyte,” but each check is red.
  The evaluator searches `output.citations` instead of `output.answer`, so it
  cannot see those facts.
- `glass_tube_replacement` is an evaluator false positive and a hollow pass. It
  is the only green fact check because `transistor` happens to appear in its
  citation slug. The answer is correct, but the verdict would remain green even
  if the prose said the opposite.
- All 12 `AnswerIsSubstantial` checks are hollow passes. `len(answer) > 15`
  rewards long refusals and nonsense, and it can reject a concise correct
  answer. It provides no trustworthy signal here.
- Those checks hide one real agent failure: the IPv4 answer says every internet
  device has an IPv4 address. The section says every device has an IP address
  and separately distinguishes IPv4 from IPv6. The deterministic fact and
  citation checks cannot detect that strengthened quantifier.
- The remaining answers state an accepted fact and cite the expected section.
  `original_text_chars` adds an unnecessary context caveat but still answers
  128 from the cited material. Because the dominant red cluster came from an
  evaluator defect, I repaired the evaluator before changing the agent.

### The improvement

- **What and why:** `AnswerMentionsFact` now checks normalized answer text, not
  citation strings. Each fact is an AND of accepted-phrasing groups. Numbers
  use whole-token boundaries, nearby negation invalidates a match, and prefix
  matching must be explicit (`encrypt*`); arbitrary words are not treated as
  stems. I replaced the length check with `ExpectedSectionCited`. Regression
  tests reject long nonsense, citation-slug-only matches, `165` for `65`,
  negated facts, arbitrary prefixes, and incomplete multi-part answers.
- **Before/after (report files):**

  - The controlled comparison,
    `eval-report-study-coach-hard-offline-rescore-2026-08-10T182400Z.json`,
    reuses the byte-identical outputs from the 25/36 baseline and applies the
    current three deterministic evaluators and metadata. It scores 36/36 with
    no model call, isolating the evaluator repair. The baseline IPv4 overreach
    remains, which shows that 36/36 deterministic assertions are not a complete
    quality claim.
  - The fresh intermediate report,
    `eval-report-study-coach-hard-2026-08-10T175523Z.json`, also scored 36/36
    but made two unsupported additions: transistors packed "by the millions"
    where the section says "many," and every device having IPv4. That hollow
    green prompted me to add the course-evidence faithfulness judge and tighten
    the agent's generic scope and quantifier rules. I did not add rules for
    either specific question.
  - The final fresh report,
    `eval-report-study-coach-hard-2026-08-10T182707Z.json`, scored 48/48: 12
    cases with four assertions each, including faithfulness. I inspected every
    raw output. The glass-tube and IPv4 answers avoid the earlier overreach.
- **Why this should generalize beyond the visible cases:** The matchers operate
  on metadata fact groups and normalized answer text, provenance uses per-run
  retrieval, and the judge sees retrieved chunks instead of case-specific
  expected prose. The offline 36/36 and fresh 48/48 use different assertion
  sets. They provide separate evidence and do not represent a linear score
  improvement. Fresh generations remain stochastic samples.

### Handoff note (ADR-style, ~half a page)

<!-- The pod rotates off; the course team's engineers run this for ~10k
     students. What changes first? What must they know? -->

**Decision: replace per-request quiz generation with versioned, reviewed quiz
authoring before scaling to 10k students.** The prototype makes one authoring
call, five concurrent isolated review calls, and bounded repair and re-review
calls when an item fails; it also sends the answer key to the browser. That is
a reasonable tradeoff for local formative learning. At course scale, this
multi-call synchronous path creates variable latency and cost, model-drift
risk, inconsistent student experiences, and no academic-integrity boundary.

The first production change should generate candidate questions against an
immutable course-material version. It should record the prompt, model, and
material hashes plus the retrieved evidence; run the deterministic and semantic
validators; and send the result to an instructor approval queue. Approved
questions become cached, immutable quiz IDs. Students receive a sampled quiz
without `correct_index`, and the server grades submissions against that ID.
This design provides predictable cost, reproducibility, trust, and operability
at the expense of per-request novelty.

Then add institutional authentication and authorization, rate limits and
quotas, attempt persistence, audit logs, latency/token/error telemetry,
automated and manual accessibility checks, and retention/privacy rules. Treat
evaluator scores as monitored evidence only; they do not establish truth.
Maintain a versioned, instructor-reviewed held-out set, calibrate the LLM judge
against human labels, inspect raw outputs after regressions, and put model or
prompt changes through that release gate. The current API is intended and
documented for localhost use. It is not hardened against external exposure
until those controls exist.
