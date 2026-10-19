# ai01 · Write a brief that gets it right the first time
The quality of what Claude Code or Codex gives you is set by the brief. Vague ask, vague result.

1. Pick a real MOTION job (e.g. "a 15 s lineup reel", "a story for the costume prize").
2. Write a brief in `brief.md` using `orch/tasks/TEMPLATE.md`: goal in one sentence, inputs (exact file paths), deliverable (format, size, where it goes), the rules that matter (from CLAUDE.md), and **done when** (how you'll check it).
3. Give it to Claude Code. Compare what you got to your "done when". Note what you'd write differently next time.

What separates a good brief:
- **Say the outcome and the check**, not the steps. "Ends on the full logo, nothing cut off at the edges" beats "make it nice".
- **Point at files**, not descriptions ("`media/flyers/final_v6/flyer_source.html`", not "the flyer").
- **Say what must not change** ("don't touch final_v6/, make an updated-draft copy").
- **One job per brief.** Split big asks.
