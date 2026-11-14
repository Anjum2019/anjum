# Fixing a blocked push (GH013 — "Push cannot contain secrets")

GitHub's push protection rejected the push because a commit in the **unpushed**
local history contains `AI Agent/.env` with a Groq API key on line 1.

The file never reached the repository, so nothing needs cleaning on GitHub —
only in your local commits.

## 1. Rotate the key first

The key was transmitted to GitHub and flagged. Treat it as compromised:

- Go to <https://console.groq.com/keys>
- Revoke the exposed key, create a new one
- Put the new key in your local `AI Agent/.env` (this file stays on disk, untracked)

## 2. Clean the local history

Run the helper from the repository root:

```bash
bash scripts/unblock-secret-push.sh
```

It will:

1. Detect every `.env` committed in the unpushed range `origin/main..HEAD`
2. Create a `backup/pre-secret-scrub-*` branch so you can undo everything
3. `git rm --cached` the file (kept on disk) and add `.env` rules to `.gitignore`
4. Rewrite **only the unpushed commits** with `git filter-branch`, deleting the
   file from each of them
5. Verify no `.env` remains in the range, and that the shared ancestor with
   `origin/main` is unchanged — so a normal fast-forward push works
6. Prune the old objects so nothing stale can be offered to the remote

Then push:

```bash
git push origin main
```

### Preview only

```bash
DRY_RUN=1 bash scripts/unblock-secret-push.sh
```

### Undo

```bash
git reset --hard backup/pre-secret-scrub-<timestamp>
```

## Manual alternative

If the secret is in the **most recent** commit, no rewriting tool is needed:

```bash
git reset --soft HEAD~1          # undo the commit, keep changes staged
git restore --staged "AI Agent/.env"
git commit -m "your message"
git push origin main
```

If it is deeper in the unpushed history, rebase onto the last pushed commit:

```bash
git log --oneline --diff-filter=A -- "AI Agent/.env"   # find the commit
git rebase -i origin/main                              # mark it 'edit'
git rm --cached "AI Agent/.env"
git commit --amend --no-edit
git rebase --continue
git push origin main
```

## Why this happened

`.gitignore` does **not** untrack a file that is already tracked. If
`AI Agent/.env` was committed before the ignore rule existed, Git keeps sending
it in every later commit — and `git add -f` bypasses ignore rules entirely.
The helper script removes it from the index (`git rm --cached`) so the existing
rule can take effect.

Your code is already correct — it reads the key from the environment rather
than hardcoding it:

```python
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
```

## Do not use the "allow secret" link

The unblock URL in the error message pushes the live key into a public-ish
history permanently. Rewriting the commit is the right fix.
