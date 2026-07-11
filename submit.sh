#!/usr/bin/env bash
# Pre-submission check (`make submit`). Verifies your work is ready and tells
# you exactly how to hand it in. Submission = your PRIVATE GitHub repo:
#   1. everything committed and pushed,
#   2. video links in SOLUTION.md,
#   3. invite the GitHub username from your invite email as a collaborator.
#
# NOT a fork: your repo must be a NEW private repository, not a fork of the
# exercise repo. Forks of public repos are always public (they'd publish your
# work and the solution) and are REJECTED automatically at import.
#
# Fallback (only if your invite told you to submit by email):
#   ./submit.sh --bundle    -> study-coach-submission.bundle (full history;
#   contains only committed content, so your .env / API key can't leak).
set -euo pipefail
cd "$(dirname "$0")"

fail() { printf '\n❌ %s\n' "$1" >&2; exit 1; }
warn() { printf '\n⚠️  %s\n' "$1" >&2; }

git rev-parse --git-dir >/dev/null 2>&1 || fail "This isn't a git repo. Did you clone the exercise repo (see README.md)?"
git rev-parse HEAD >/dev/null 2>&1 || fail "No commits yet. Commit your work first (we review the history)."

# Uncommitted work won't be reviewed.
if ! git diff --quiet || ! git diff --cached --quiet; then
  warn "You have uncommitted changes — they will NOT be reviewed. Commit them first."
fi

# Eval reports are expected.
if ! ls evals/reports/*.json >/dev/null 2>&1; then
  warn "No eval reports found in evals/reports/. You were asked to commit them — run 'make evals' and commit."
fi

# Both video links are required — a submission without them will not advance.
video_line() { grep -A0 "^- $1" SOLUTION.md 2>/dev/null | head -1 | sed "s/^- $1[^:]*: *//"; }
V1="$(video_line 'Walkthrough' || true)"
V2="$(video_line 'AI workflow' || true)"
if [ -z "$V1" ] || [ -z "$V2" ]; then
  fail "SOLUTION.md is missing one or both video links (the 'Video links' section).
   Both videos are required — paste the links, or write 'sent by email' there
   if you're emailing the files instead, then commit."
fi

if [ "${1:-}" = "--bundle" ]; then
  OUT="study-coach-submission.bundle"
  git bundle create "$OUT" --all >/dev/null
  printf '\n✅ Created %s (%s)\n' "$OUT" "$(du -h "$OUT" | cut -f1)"
  printf '   Email this one file back per your invite. Your videos are not in the\n'
  printf '   bundle — links in SOLUTION.md, or send the files with it.\n'
  exit 0
fi

# Repo flow: origin must be YOUR private repo, not the public exercise repo.
ORIGIN="$(git remote get-url origin 2>/dev/null || true)"
[ -n "$ORIGIN" ] || fail "No 'origin' remote. Create a NEW PRIVATE repo under your GitHub
   account (NOT a fork), then:  git remote add origin <your-repo-url> && git push -u origin main"
case "$ORIGIN" in
  *MAS-SNHU/study-coach-exercise*|*MAS-SNHU/*)
    fail "Your 'origin' still points at the exercise repo ($ORIGIN).
   Submit from your OWN private repo:  git remote set-url origin <your-repo-url> && git push -u origin main" ;;
esac

# Everything pushed?
if git rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
  AHEAD="$(git rev-list --count '@{u}..HEAD')"
  [ "$AHEAD" = "0" ] || warn "$AHEAD commit(s) not pushed yet — run: git push"
else
  warn "Current branch has no upstream — run: git push -u origin $(git branch --show-current)"
fi

printf '\n✅ Ready to submit. Final three steps:\n'
printf '   1. Make sure your repo is PRIVATE and is NOT a fork (forks are rejected\n'
printf '      automatically — if you forked, create a fresh private repo and push there).\n'
printf '   2. Invite the GitHub username from your invite email as a collaborator\n'
printf '      (your repo → Settings → Collaborators → Add people).\n'
printf '   3. Reply to your invite email with your repo URL.\n'
