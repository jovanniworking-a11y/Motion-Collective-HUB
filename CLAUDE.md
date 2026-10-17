# MOTION Collective HUB — working rules for Claude

## Route every task
Start every reply to a new task with one line: **Route: <bot> — <why>**. If parts go to different bots, list each part.

| Bot | Use it for |
|---|---|
| **Claude Code** (this repo / cloud session) | Code, the hub (`hub.py`, `web/`), Room Studio changes, spreadsheets/builders, GitHub, Drive/Gmail/Calendar lookups, pulling files together |
| **Claude chat** (project "MOTION EFFEcts") | Decisions, Source of Truth edits, design review, run of show, anything that needs the full project history |
| **ChatGPT** | Quick copy: IG captions, DMs, texts to artists/neighbours, fast price checks |
| **Gemini** | Watching video/reels and long clips, comparing images, auditing big Drive sheets |
| **Codex** (on Jovanni's PC) | Work on files that only exist on the PC (`C:\Users\jyanez\...`), running local scripts |
| **Higgsfield** | AI video shots (doc 06 shot list) |
| **Adobe Express** | Final flyer / story / post layouts for export |

## Hard rules (from the Source of Truth + Agent Playbook)
- The venue address never goes in any file, post or page.
- No unconfirmed names on promo. Rohan Rali is cut (14 Oct). Glamz confirmed 16 Oct and plays SOLO in the middle (17 Oct; credit wording still to confirm). Order: iamariology b2b raymixes → Glamz → HE//THEY. HE//THEY is credited exactly "HE//THEY · co.b b2b NiiON".
- Never spend, send, post or publish without Jovanni's OK. Draft only.
- No YSL marks, no haze/fog, no lasers. Bodoni Moda + Jost. Red ≤ 10% of the frame.
- Label every number confirmed / estimate / open.
- Guest data stays out of git.

## Design rules Jovanni has corrected (don't repeat these)
- **Red is an accent, never a tint.** Use it only for small marks: the MMMM trail, thin rules, and labels like "b2b" / "b3b" under or between artist names. Never colour an image, photo, video frame or the eyes red.
- Images and video stay black and white / steel blue, like the eyes teaser.
- Check source images for baked-in text or logos before laying type over them (the teaser eyes already contain "10.30.26" and MMMM).
- Render and look at every export at full size before sending; check nothing is cut off at the edges.
- No set times on promo unless Jovanni asks for them (SoT rule); offer them only as a separate variant.
- Test pages in a real (headless) browser, not just a syntax check, before saying they work.

## Where things are
- Web hub: https://claude.ai/artifact/6nZX6PmhuCXFezNSu6gkfM (source `web/index.html`, data seeded from `web/seed.json`)
- Room Studio: https://claude.ai/artifact/49y1uMCWh1em8QAfMbvBiV
- Fan site (public once shared): https://claude.ai/artifact/Fjd1GpHBNFyu21EJtNBCgB (source `site/index.html`; content lives in the page's `motion-state` JSON; owner edits via "Edit site")
- RSVP: Tally form https://tally.so/r/Ekj7zA · Instagram @motioncollective.atx
- Python hub: `python hub.py` (catalog, event learning, Excel export)
- Agent kit + project context: `orch/`
