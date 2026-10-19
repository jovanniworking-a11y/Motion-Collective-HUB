# ai02 · Turn your rule into a skill
Every time you correct the AI, that correction should become permanent. In this repo that happens three ways:
`CLAUDE.md` (rules read every session), `orch/creative/taste.json` (your taste, dated), and skills in `.claude/skills/` (step-by-step playbooks).

1. Read `.claude/skills/motion-promo/SKILL.md` to see how a skill is written: a name, a one-line description of when to use it, then the steps.
2. Write a new skill, `.claude/skills/motion-qc/SKILL.md`: "before sending any video: run `media/posts/montage_b2b/src/qc.py`, look at every 3rd frame, check edges, check the end card…" (use the finishing pass we did on the b2b reel as your source).
3. In a new Claude Code session, say "QC this video" and see if it follows your skill.

Read: code.claude.com/docs, the "Skills" and "Memory / CLAUDE.md" pages.
