# Study Coach — AI Engineering Work Sample

Welcome! This exercise simulates the kind of work our AI Engineering pods do:
you've just rotated onto a small embedded team. **Study Coach** is a prototype
AI study assistant for the fictional course *CS-1010: Foundations of
Computing* — students chat with it about the course materials and it answers
with citations. The previous engineer left it partially working: some things
are broken, one feature is missing, and the team needs you.

We designed this to respect your time and to let you work the way you
actually work — **AI coding tools are required, not just allowed.**

## Time commitment (honest numbers)

| Phase | Budget | On the clock? |
|---|---|---|
| Setup + reading this repo | ~30 min typical | No — untimed |
| Coding (the tasks in TASKS.md) | **90 min (mid) / 120 min (senior)** | Yes |
| SOLUTION.md polish + two short videos | ~45 min | No — untimed |

Total: roughly 2.5–3 hours. The coding window works on the honor system,
observed via your commit timestamps: make your first commit when you start and
commit as you go (small, frequent commits — we read the history). Work beyond
the window isn't rewarded: the rubric scores judgment and communication, not
volume, and reviewers treat obviously-over-budget polish as a negative signal.
When time runs out, stopping and writing down what you'd do next scores
better than silently overrunning.

## Rules

- **Use your AI coding tools throughout.** Claude Code or Codex preferred;
  Cursor is fine. We're hiring for AI-augmented engineering — show us your
  real workflow, including where you overrode or corrected the tool.
- Any resources you like (docs, search). No other people.
- **Keep your work private.** The exercise repo is public; your solution must
  not be. Your repo must be **private**, and **never a fork** (see the warning
  below). Don't publish or share your solution anywhere else either.
- Everything you claim must be verifiable from what you commit. We re-check
  your committed eval reports against your recorded outputs, so commit them
  (`evals/reports/`) and make sure your numbers are real.

## Setup (untimed — take your time)

### ⚠️ CLONE, don't fork — forks are rejected

**Do not click GitHub's Fork button.** A fork of a public repo is itself
**public** — it would publish your work (and the solution) to the world, so
**forked submissions are rejected automatically** and you'd be asked to
redo the submission steps. Instead:

```bash
# 1. Clone the exercise (note: clone, NOT fork)
git clone https://github.com/MAS-SNHU/study-coach-exercise.git
cd study-coach-exercise

# 2. Create a NEW PRIVATE repo under your own GitHub account (any name is
#    fine). Via github.com: New repository → Private → no README. Or:
#    gh repo create study-coach --private

# 3. Point this clone at YOUR repo and push
git remote set-url origin git@github.com:<your-username>/study-coach.git
git push -u origin main
```

That's the whole trick: our history stays, your work goes to your private
repo, nothing is public. Commit and push as you go — the history is part of
what we read. (If you received this as a zip instead, unzip it and start from
the same point — it's already a git repo.)

Prerequisites: [uv](https://docs.astral.sh/uv/), Node 20+, and an Anthropic
API key.

**Getting an API key:** if you don't already have one, create an account at
https://console.anthropic.com and generate a key. API usage is paid, but this
exercise is tiny — a few dollars of usage at most. **If obtaining or funding a
key is a barrier for you in any way, email your recruiting contact before you
start** — we'll make sure you're not blocked. API access isn't part of what
we're assessing, and we don't want you spending time or money to get it.

```bash
make setup            # installs backend + frontend dependencies
cp .env.example .env  # then paste your API key into .env
make verify-setup     # everything green? you're ready
```

Your `.env` holds your API key — it's already in `.gitignore`; keep it that
way and don't commit it. (Standard practice; noted here just so nothing's a
surprise.)

Useful commands (also in `CRIB_SHEET.md`, along with a one-page intro to the
two libraries this repo uses — no prior experience with them is assumed):

```bash
make test          # pytest — needs NO API key
make evals         # eval suite — needs the key; writes evals/reports/*.json
make dev-backend   # API on :8000
make dev-frontend  # web app on :5173
```

Python note: we use Python day to day, but we hire for engineering judgment,
not stack trivia — the codebase is small and your AI tools know the idioms.

## What to do

Open **TASKS.md**. Start the clock at your first commit.

## Deliverables & how to submit

1. **Your commits** — commit as you work; the history is part of what we read.
2. **SOLUTION.md** filled in (template provided — keep it tight), including
   your two **video links** in the "Video links" section.
3. **Committed eval reports** from your runs (`evals/reports/`).
4. **Two screen recordings, ≤5 minutes each** (see below), hosted anywhere;
   put the links in SOLUTION.md.

When you're done, run:

```bash
make submit        # checks you're ready and prints the final steps
```

Then submit in three steps (`make submit` walks you through them):

1. **Push everything** to your **private** repo (remember: yours, not a fork —
   forked submissions are rejected automatically).
2. **Invite the GitHub username from your invite email** as a collaborator on
   your repo (Settings → Collaborators → Add people) so we can review it.
3. **Reply to your invite email with your repo URL.**

Your `.env` is gitignored, so your API key never leaves your machine.

**Both videos are required — a submission without them is incomplete and will
not advance.** Host them and put the links in SOLUTION.md (preferred), or
email the files with your submission reply. Don't commit large video files
into the repo.

(Only if your invite specifically said to submit by email: `make bundle`
creates `study-coach-submission.bundle` — send that one file back instead.)

### The videos

Screen recording with voiceover. Your face is never required, any recording
tool is fine (Loom, QuickTime, OBS…), re-records are allowed, and production
quality doesn't matter — we're listening to your reasoning, not your editing.
Share links or files per your recruiter's instructions.

**Video 1 — understanding walkthrough.** Must cover: (a) the root cause of
the bug that the *evals* caught and why the unit tests couldn't catch it;
(b) the scope decision in your feature you're least sure about, and what
you'd ask the Product Owner; (c) one piece of code your AI tool wrote that
you changed or rejected, and why.

**Video 2 — your AI workflow.** Show how you actually worked on one part of
this exercise — live capture or a narrated replay of your real session, either
is fine. We're interested in your real working relationship with the tool, not
a polished demo. Good things to show (pick what's genuine to how you worked —
you don't need all of them):

- a moment you steered or corrected the tool, or where its output was wrong,
  incomplete, or subtly off — and how you caught it and what you did;
- a suggestion you decided *not* to take, and why;
- how you verified something before trusting it (a test, a doc, reading the
  code) rather than accepting it on faith;
- a judgment call the tool couldn't make for you — scoping, a tradeoff, naming,
  when to stop;
- how you set the tool up to be useful (context you gave it, how you broke the
  work down, prompts or a workflow you've refined over time).

If there's one thread we care about most, it's evidence that you drive and
validate the tool rather than just accept what it produces.

**Accommodation:** if recording narrated video is a barrier for you for any
reason, tell your recruiter — you can cover the same two outlines in a short
live call with a reviewer instead. This is a full substitute and doesn't
affect scoring.

## How you'll be evaluated

Eight dimensions, equally grounded in your code, commits, SOLUTION.md, eval
reports, and videos: debugging and root-cause reasoning · product/scope
judgment · **eval craft** (we care a lot about this — write evals that target
failures you actually observed, not generic ones) · agent/LLM implementation
quality · full-stack execution · security thinking · AI-workflow fluency ·
communication and ownership. Senior candidates: your track includes an
error-analysis exercise; a **hidden held-out eval set** is run against your
final commit, so fixes that generalize beat fixes that memorize the visible
cases.

If your submission advances, expect a short follow-up call where you'll make a
small live change to your own code - it's a standard gate for everyone who
moves forward, not a bad sign.

Questions or something broken in the repo? Email your recruiting contact.
Good luck — we hope this is fun.
