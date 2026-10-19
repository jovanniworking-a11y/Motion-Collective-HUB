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
- Artists (iamariology, raymixes and the lineup) OK'd posting their clips (17 Oct). Guests' faces in crowd shots still need care.
- No unconfirmed names on promo. Rohan Rali is cut (14 Oct). Glamz confirmed 16 Oct and plays SOLO in the middle (17 Oct; credit wording still to confirm). Order: iamariology b2b raymixes → Glamz → HE//THEY. HE//THEY is credited exactly "HE//THEY · co.b b2b NiiON".
- Never spend, send, post or publish without Jovanni's OK. Draft only.
- No YSL marks, no haze/fog, no lasers. Bodoni Moda + Jost. Red ≤ 10% of the frame.
- Label every number confirmed / estimate / open.
- Guest data stays out of git.
- Effects: we rebuild looks from published methods of open-source tools (notes in `orch/creative/research/oss_effects_algorithms.md`); never copy GPL code into the repo and never download or redistribute paid plugins.

## Design rules Jovanni has corrected (don't repeat these)
- **Red is an accent, never a tint.** Use it only for small marks: the MMMM trail, thin rules, and labels like "b2b" / "b3b" under or between artist names. Never colour an image, photo, video frame or the eyes red.
- Images and video stay black and white / steel blue, like the eyes teaser.
- Check source images for baked-in text or logos before laying type over them (the teaser eyes already contain "10.30.26" and MMMM).
- Render and look at every export at full size before sending; check nothing is cut off at the edges.
- No set times on promo unless Jovanni asks for them (SoT rule); offer them only as a separate variant.
- Test pages in a real (headless) browser, not just a syntax check, before saying they work.
- Edits must feel directed, not random: every cut has a reason (motion, eye-trace, graphic, music, story), build density then release on the drop, real motion blur, one grade. Direction (Jovanni, 17 Oct): pop-culture edit language, not corporate. References: Lucki, Peso Pluma, Kanye set design, Yeat graphics, Carti, Prospa, Kettama, Boiler Room, Raw Cuts, Drake, Bad Bunny / reggaeton. The mix of all of them. Warps, fisheye, glitch, type stacks and camcorder HUD are ON brand; still never CapCut presets on every cut, and red never tints footage.
- The logo is the dimensional mark (`media/brand/`), never flat overlapping type.
- Every cut is a new shot (Charvel + Abraham, 18 Oct): never cut back to the same angle 2-3 times; an angle returns only when the story needs it. Cut faster rather than recycle. Zooms and effects on the artists are fine. Every edit carries AFTERIMAGE branding and the 3x eyes.
- A b2b is two equal stars (19 Oct): same name size and treatment for both, one featured moment each. Small type at least 30 px on a 1080 frame.

## Where things are
- Web hub: https://claude.ai/artifact/6nZX6PmhuCXFezNSu6gkfM (source `web/index.html`, data seeded from `web/seed.json`)
- Room Studio: https://claude.ai/artifact/49y1uMCWh1em8QAfMbvBiV
- Fan site (public once shared): https://claude.ai/artifact/Fjd1GpHBNFyu21EJtNBCgB (source `site/index.html`; content lives in the page's `motion-state` JSON; owner edits via "Edit site")
- FX Library (effects gallery + cut rules + crew loop): https://claude.ai/artifact/2Wn5UpD5rwZaQ9XsBUFFeH (source `media/fx/gallery.html`, effects code `media/fx/mfx.py`)
- Video direction: `orch/creative/DIRECTORS_BIBLE.md` (every cut needs a reason; read before any edit). Logo: `media/brand/` (dimensional mark), sting `media/sting/`
- RSVP: Tally form https://tally.so/r/Ekj7zA · Instagram @motioncollective.atx
- Python hub: `python hub.py` (catalog, event learning, Excel export)
- Agent kit + project context: `orch/`
- Learning track (Python, ML, using AI tools): `learn/` (`python learn/check.py all`). When Jovanni asks for help with an exercise, explain and give hints; don't write the solution unless he asks.
- Taste profile (references, loves, hates, corrections): `orch/creative/taste.json`. Promo/creative-direction skill: `.claude/skills/motion-promo/SKILL.md` (use it whenever Jovanni asks to promote something or describes a vibe)
