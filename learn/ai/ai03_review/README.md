# ai03 · Stay the director: the review loop
AI-guided, not AI-generated, means you review every change. A 5-minute loop:

1. **Before:** say what you want and how you'll check it (ai01).
2. **After:** run `git diff` (or ask "show me the diff and explain each change in one line").
3. **Ask why** about anything you don't understand. If the answer is vague, that's usually where the bug is.
4. **Check it yourself**: render, open the page, run the check. Never take "it works" on faith (that's a rule in CLAUDE.md for a reason).
5. **Correct once, permanently**: if you had to fix its taste, add the rule to `taste.json` or a skill (ai02).

Practice: pick any commit from this repo's history (`git log --oneline`), run `git show <id>`, and explain it back in three lines. Then ask Claude to grade your explanation.

Using several AIs well (your routing table in CLAUDE.md):
- **Claude Code**: anything in the repo, multi-step work, edits you can verify.
- **Codex**: files that only live on your PC; give it the exact path and a done-when.
- **Claude chat / ChatGPT / Gemini**: decisions, quick copy, watching long video.
- Hand work between them with briefs (ai01), not with "remember what we said".
