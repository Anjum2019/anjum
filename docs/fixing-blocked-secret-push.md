# Fixing a leaked Groq key and a blocked push (GH013)

There are **two separate problems**, and the first one is the urgent one.

---

## Problem 1 — a live Groq key is already public in this repository

A key was committed in `4aa4715` ("first commit", 2026-10-11) as `AI Agent/.env`,
and it is reachable from **`main`**, `AI_agent`, and `AI_agnet_2`:

```
GROQ_API_KEY=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
```

It appears in 6 commits across 30 reachable commits. Commit `3d69366`
("Remove .env from repo and add to .gitignore") deleted the file from the *tip*,
but deleting a file does not remove it from history — the blob is still served
by GitHub and has been public since 2026-10-11. PRs #1 and #2 were merged from
the two affected branches.

### Step 1 — revoke the key (this is the actual fix)

<https://console.groq.com/keys> → revoke `gsk_ljBX…XXY` → create a new key →
put the new one in your local `AI Agent/.env`.

**History rewriting does not un-leak a key.** GitHub serves commits by SHA even
after they become unreachable, forks and clones made since 2026-10-11 still
contain it, and merged PR pages keep their diffs. Rewriting history is hygiene;
revoking the key is remediation. Do the revoke first.

### Step 2 — optionally scrub the history

Verified against a full clone: this removes all 6 occurrences and leaves the
`main` tip byte-identical (55 files, 29 `.py`).

```bash
git clone https://github.com/Anjum2019/anjum.git anjum-clean
cd anjum-clean
git fetch origin '+refs/heads/AI_agent:refs/heads/AI_agent' \
                 '+refs/heads/AI_agnet_2:refs/heads/AI_agnet_2'

FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force \
  --index-filter 'git rm -r --cached --ignore-unmatch -- "AI Agent/.env"' \
  --prune-empty -- --all

git for-each-ref --format='%(refname)' refs/original/ \
  | xargs -n1 -r git update-ref -d
git reflog expire --expire=now --all
git gc --prune=now

# confirm: must print 0
git rev-list --all | while read c; do
  git grep -a -I -nE 'gsk_[A-Za-z0-9]{20,}' "$c" -- 2>/dev/null
done | wc -l

git push --force origin main AI_agent AI_agnet_2
```

This **force-pushes and rewrites shared history** on three branches, changing
every commit SHA. Anyone else with a clone must re-clone. Ask GitHub Support to
clear cached commit views afterwards.

---

## Problem 2 — the blocked push

```
remote: error: GH013: Push cannot contain secrets
remote:      —— Groq API Key ——
remote:          - commit: be4865182d052021960d634f9e25f33d5a1c5816
remote:            path: AI Agent/.env:1
```

Commit `be486518` exists **only on your machine** — it is not on GitHub
(`git ls-remote origin` does not list it). Push protection scans what you are
*about* to send and refused it. Fix it locally:

```bash
# if the secret is in your most recent commit
git reset --soft HEAD~1
git restore --staged "AI Agent/.env"
git commit -m "your message"
git push origin main
```

If it is deeper in the unpushed history:

```bash
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force \
  --index-filter 'git rm -r --cached --ignore-unmatch -- "AI Agent/.env"' \
  --prune-empty -- origin/main..HEAD
git push origin main
```

Or run the helper, which also backs up your branch and verifies the result:

```bash
bash scripts/unblock-secret-push.sh
```

Then push. Do **not** use the "allow secret" URL from the error — that writes a
live key into history permanently.

---

## Why `.gitignore` did not protect you

`.gitignore` does not untrack a file that is already tracked. Once `.env` is in
the index, Git keeps sending it in every commit, and `git add -f` bypasses the
rule entirely. Clear it from the index once:

```bash
git rm --cached "AI Agent/.env"
```

The code itself is already correct — it reads from the environment:

```python
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
```
