#!/usr/bin/env bash
#
# fix-env-push.sh  —  run in Git Bash on Windows ("C:\Program Files\Git")
#
# Fixes the repeated "GH013: Push cannot contain secrets" rejection.
#
# Why it keeps happening: AI Agent/.env is TRACKED in your index. VS Code shows
# it as a change, you commit it, and the new commit still contains the key, so
# GitHub rejects the push again with a different SHA each time. .gitignore has
# no effect on a file that is already tracked.
#
# This script backs up your branch, collapses your unpushed commits into one
# clean commit without the .env, verifies no key remains, and pushes.
#
#   bash scripts/fix-env-push.sh            # fix and push
#   DRY_RUN=1 bash scripts/fix-env-push.sh  # everything except the push

set -uo pipefail   # deliberately NOT -e: git grep returns 1 when it finds nothing

SECRET_PATH="${SECRET_PATH:-AI Agent/.env}"
MESSAGE="${MESSAGE:-Update AI Agent work (.env untracked)}"
DRY_RUN="${DRY_RUN:-0}"

say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m  ok\033[0m %s\n' "$*"; }
bad()  { printf '\033[1;31m  !!\033[0m %s\n' "$*" >&2; }

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { bad "Not a git repository."; exit 1; }
ok "Repository: $ROOT"

git rev-parse --verify origin/main >/dev/null 2>&1 || { bad "No origin/main. Run: git fetch origin"; exit 1; }

# ------------------------------------------------------------- stale lock file
LOCK="$(git rev-parse --git-dir)/index.lock"
if [ -e "$LOCK" ]; then
  say "Removing stale lock: $LOCK"
  rm -f "$LOCK" || { bad "Could not remove the lock. Close VS Code and retry."; exit 1; }
  ok "Lock removed."
else
  ok "No index.lock present."
fi

# ------------------------------------------------------------- safety backup
BACKUP="backup/pre-env-fix-$(date +%Y%m%d-%H%M%S)"
git branch "$BACKUP" HEAD || { bad "Could not create backup branch."; exit 1; }
ok "Backup branch: $BACKUP   (undo: git reset --hard $BACKUP)"

ORIGIN_MAIN="$(git rev-parse origin/main)"
UNPUSHED="$(git rev-list --count origin/main..HEAD)"
ok "origin/main=${ORIGIN_MAIN:0:7}, unpushed commits: $UNPUSHED"

# -------------------------------------------------------- .gitignore coverage
touch .gitignore
ADDED=""
for rule in '.env' '.env.*' '!.env.example'; do
  grep -qxF -- "$rule" .gitignore || { printf '%s\n' "$rule" >> .gitignore; ADDED="$ADDED $rule"; }
done
[ -n "$ADDED" ] && ok "Added ignore rules:$ADDED" || ok ".gitignore already ignores .env"

# ------------------------------------- collapse unpushed history into one commit
say "Collapsing $UNPUSHED unpushed commit(s) into one clean commit"
git reset --soft origin/main || { bad "git reset failed."; exit 1; }

# Untrack the secret. The file on disk is NOT deleted.
git rm -r --cached --ignore-unmatch -- "$SECRET_PATH" >/dev/null
ok "Untracked '$SECRET_PATH' (still on disk)"

git add -A
git commit -q -m "$MESSAGE" || { bad "git commit failed - nothing to commit."; exit 1; }
ok "Committed."

# ------------------------------------------------------------------- verify
say "Verifying no Groq key remains in what will be pushed"
LEAKS="$(git rev-list origin/main..HEAD \
  | while read -r c; do git grep -a -I -nE 'gsk_[A-Za-z0-9]{20,}' "$c" -- 2>/dev/null; done)"
if [ -n "$LEAKS" ]; then
  bad "Key still present - NOT pushing:"
  printf '%s\n' "$LEAKS" | sed 's/^/      /' >&2
  bad "Restore with: git reset --hard $BACKUP"
  exit 1
fi
ok "No gsk_ key in any commit to be pushed."

if [ -n "$(git ls-files -- "$SECRET_PATH")" ]; then
  bad "'$SECRET_PATH' is still tracked."; exit 1
fi
ok "'$SECRET_PATH' is untracked."

git merge-base --is-ancestor origin/main HEAD \
  || { bad "Not a fast-forward. Restore: git reset --hard $BACKUP"; exit 1; }
ok "Fast-forward push is safe."

if [ "$DRY_RUN" = "1" ]; then
  printf '\033[1;33m\nDRY_RUN=1 - not pushing. Push with: git push origin main\033[0m\n'
  exit 0
fi

say "Pushing"
git push origin main || { bad "Push rejected. Restore: git reset --hard $BACKUP"; exit 1; }

printf '\n'
ok "Pushed. .env stayed on your disk."
printf '\033[1;33mREMINDER: revoke the exposed key at https://console.groq.com/keys\033[0m\n'
printf '\033[1;33mIt is still in this repository'"'"'s public history on main.\033[0m\n'
