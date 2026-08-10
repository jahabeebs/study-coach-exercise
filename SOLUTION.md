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

### Questions I'd ask the Product Owner

### Evals

- Observed failures/near-misses from running my feature (2–3 examples, paste
  the actual outputs):
- Which evaluator targets which observed failure:

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
