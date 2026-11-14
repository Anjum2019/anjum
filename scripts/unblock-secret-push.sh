#!/usr/bin/env bash
#
# unblock-secret-push.sh
#
# Fixes a GitHub "GH013: Push cannot contain secrets" rejection caused by a
# .env file that was committed into *unpushed* local history.
#
# It does three things:
#   1. Makes sure .env is ignored and untracked from now on.
#   2. Rewrites ONLY the commits that have not been pushed yet, dropping the
#      secret file from every one of them.
#   3. Verifies the file is gone from the range you are about to push.
#
# It never touches commits that are already on GitHub, so no force-push and no
# coordination with collaborators is needed.
#
# Usage:
#   bash scripts/unblock-secret-push.sh                 # detect + fix .env files
#   bash scripts/unblock-secret-push.sh "path/to/.env"  # fix an explicit path
#
# Env overrides: REMOTE=origin BRANCH=main DRY_RUN=1

set -euo pipefail

REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-main}"
DRY_RUN="${DRY_RUN:-0}"

say()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m  ok\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m !! %s\033[0m\n' "$*" >&2; }
die()  { printf '\033[1;31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }

git rev-parse --git-dir >/dev/null 2>&1 || die "Run this from inside your git repository."

# ---------------------------------------------------------------- 0. sanity
git fetch "$REMOTE" "$BRANCH" --quiet 2>/dev/null || warn "Could not fetch $REMOTE/$BRANCH; using local ref."
git rev-parse --verify "$REMOTE/$BRANCH" >/dev/null 2>&1 \
  || die "No $REMOTE/$BRANCH ref found. Set BRANCH= / REMOTE= to match your setup."

BASE="$(git rev-parse "$REMOTE/$BRANCH")"
HEAD_SHA="$(git rev-parse HEAD)"
ok "Already-pushed tip ($REMOTE/$BRANCH): ${BASE:0:7}"
ok "Your local tip            (HEAD): ${HEAD_SHA:0:7}"

if [ "$BASE" = "$HEAD_SHA" ]; then
  warn "Nothing is unpushed on this branch, so there is no local commit to clean."
  warn "The secret must be in a different branch or an older, already-pushed commit."
fi

UNPUSHED_COUNT="$(git rev-list --count "$BASE"..HEAD || echo 0)"
say "$UNPUSHED_COUNT unpushed commit(s) in range ${BASE:0:7}..HEAD"

if [ "$UNPUSHED_COUNT" -eq 0 ]; then
  die "No unpushed commits. Nothing to rewrite. See the notes printed by the caller."
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  die "Working tree has uncommitted changes. Commit or 'git stash' them first, then re-run."
fi

# ------------------------------------------------- 1. work out what to strip
if [ "$#" -gt 0 ]; then
  OFFENDERS=("$@")
  say "Using secret path(s) given on the command line."
else
  say "Scanning the unpushed commits for committed .env files..."
  # Every path present in ANY tree in the unpushed range, filtered to .env files.
  mapfile -t OFFENDERS < <(
    git rev-list "$BASE"..HEAD \
      | while read -r c; do git ls-tree -r --name-only "$c"; done \
      | sort -u \
      | grep -E '(^|/)\.env(\.[A-Za-z0-9_-]+)?$' \
      | grep -v '\.env\.example$' \
      || true
  )
fi

if [ "${#OFFENDERS[@]}" -eq 0 ]; then
  warn "No .env file found in the unpushed range."
  warn "GitHub may be flagging a different file type. Re-run passing the path, e.g.:"
  warn "  bash scripts/unblock-secret-push.sh \"path/to/file\""
  exit 0
fi

printf '  secret file(s) to purge:\n'
for p in "${OFFENDERS[@]}"; do printf '    - %s\n' "$p"; done

if [ "$DRY_RUN" = "1" ]; then
  say "DRY_RUN=1 — stopping here, nothing changed."
  exit 0
fi

# ---------------------------------------------------- 2. keep it out going fwd
BACKUP_BRANCH="backup/pre-secret-scrub-$(date +%Y%m%d-%H%M%S)"
git branch "$BACKUP_BRANCH" HEAD
ok "Safety backup branch created: $BACKUP_BRANCH"

# Ensure the repo ignores .env at every level.
GITIGNORE=".gitignore"
touch "$GITIGNORE"
ADDED_RULES=0
for rule in '.env' '.env.*' '!.env.example'; do
  if ! grep -qxF -- "$rule" "$GITIGNORE"; then
    printf '%s\n' "$rule" >> "$GITIGNORE"
    ADDED_RULES=1
  fi
done

# Stop tracking any secret file that is currently tracked, and commit the
# .gitignore change if we had to add rules.
UNTRACKED_ANY=0
for p in "${OFFENDERS[@]}"; do
  if git ls-files --error-unmatch "$p" >/dev/null 2>&1; then
    git rm --cached --quiet -- "$p"
    ok "Untracked (file kept on disk): $p"
    UNTRACKED_ANY=1
  fi
done

if [ "$ADDED_RULES" = "1" ] || [ "$UNTRACKED_ANY" = "1" ]; then
  git add "$GITIGNORE"
  git commit --quiet -m "chore: ignore .env and untrack secrets"
  ok "Committed .gitignore / untrack change."
  HEAD_SHA="$(git rev-parse HEAD)"
fi

# ------------------------------------- 3. rewrite the unpushed range only
say "Rewriting ${BASE:0:7}..HEAD to delete the secret file from every commit..."

RM_ARGS=""
for p in "${OFFENDERS[@]}"; do
  # %q shell-escapes each path (handles the space in "AI Agent/"); the literal
  # "--" separator is added in the command string below, not here.
  RM_ARGS="$RM_ARGS $(printf '%q\n' "$p")"
done

# filter-branch is built into git (no pip/npm install needed). We scope it to
# the unpushed range so published history is left byte-for-byte identical.
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch \
  --force \
  --index-filter "git rm -r --cached --ignore-unmatch $RM_ARGS" \
  --prune-empty \
  -- "$BASE"..HEAD >/dev/null

# Drop the filter-branch bookkeeping refs it leaves behind.
git for-each-ref --format='%(refname)' refs/original/ \
  | while read -r r; do git update-ref -d "$r"; done

# --------------------------------------------------------- 4. verify + clean
STILL_THERE="$(
  git rev-list "$BASE"..HEAD \
    | while read -r c; do git ls-tree -r --name-only "$c"; done \
    | sort -u \
    | grep -E '(^|/)\.env(\.[A-Za-z0-9_-]+)?$' \
    | grep -v '\.env\.example$' \
    || true
)"

if [ -n "$STILL_THERE" ]; then
  die "Secret file still present after rewrite: $STILL_THERE — restore with: git reset --hard $BACKUP_BRANCH"
fi
ok "Verified: no .env file exists in any commit in ${BASE:0:7}..HEAD"

# Base commit must be untouched, otherwise the push would be non-fast-forward.
NEW_BASE="$(git merge-base "$REMOTE/$BRANCH" HEAD)"
[ "$NEW_BASE" = "$BASE" ] || die "Rewrite moved the shared ancestor — aborting. Restore: git reset --hard $BACKUP_BRANCH"
ok "Shared ancestor unchanged ($BASE) — a normal fast-forward push will work."

# Purge the old objects so nothing stale can be offered to the remote.
git reflog expire --expire=now --all
git gc --prune=now --quiet
ok "Old objects pruned from the local object store."

echo
ok "History is clean. Now push:"
echo
echo "    git push $REMOTE HEAD:$BRANCH"
echo
warn "Rotate the leaked Groq key at https://console.groq.com/keys — it reached"
warn "GitHub's servers and must be treated as compromised."
