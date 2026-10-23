# CLAUDE.md — orchestrator duties
- Live lock = `orch/context/CURRENT_LOCK.md` (21 Oct 2026). It wins over older paragraphs in `context/SOURCE_OF_TRUTH_latest.md`.
- Source of truth mirror stays in that file for history. Only Claude edits the body; the lock header is not optional.
- Split Jovanni's asks into tasks; brief with `tasks/TEMPLATE.md`; route per README table; review outputs against README hard rules + Agent Playbook (doc 07) before telling Jovanni they're done.
- Anything that spends, sends, posts or names a person → ask Jovanni first.
- After each merge: update BOARD.md and the Night Report / Room Studio artifact if numbers changed. Run `python3 orch/hygiene/scan.py` before saying the tree is clean.
