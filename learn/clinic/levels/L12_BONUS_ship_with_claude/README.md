# ⭐ Bonus: ship a feature with Claude Code · 300 XP
The real skill now: directing an AI to build something correct, and staying the one in charge.

The feature: **"reminders that actually send"**. Your level-6 code builds the text; now make the boss app (level 10) gain a
`remind YYYY-MM-DD HH:MM` command that prints every reminder due at that moment (no real sending yet, just print).

1. Write the brief in `notes.md` under `## Brief`: the goal, the exact files, what must not change, and **done when**.
2. Give the brief to Claude Code. Let it write the code **and a test**.
3. Review: read the diff, ask "why" about anything unclear, run `python learn/clinic/play.py` to see nothing broke.
4. In `notes.md` under `## What I checked`, write what you verified yourself, and under `## What I'd brief differently`,
   one thing you'd change next time.

The check passes when all three sections exist with real content (at least 2 lines each) and levels 6 and 10 still pass.
