# MOTION · Devil's Night — RSVP Form Setup & Copy
Written 13 Oct 2026, in response to: "want to have a link to a form to get headcount... it goes to our set list so I can get a better idea."

## Why not a Claude artifact form
I looked hard at building this as a live Claude page instead of a Google Form. The blocker: a Claude artifact's shared data store only lets people **in your org, or invited by email, write to it** — a stranger opening a public link can read a page but can never save data to it. Since your invite list is going out over Instagram DMs to people with no Claude account, that write would silently fail for basically everyone who opens it. Wrong tool for a public RSVP.

**Google Forms is the right fit:** zero account needed to submit, free, responses land in a Sheet automatically, and it's a 2-minute setup. Here's exactly what to put in it.

## Setup (you do this part — takes ~2 min)
1. Go to forms.google.com → Blank form.
2. Title and fields below — copy-paste straight in.
3. Settings (gear icon) → Responses → turn ON "Collect email addresses" **OFF** (keep it frictionless) and leave "Limit to 1 response" off unless you want to block people from updating their headcount later.
4. Responses tab → green Sheets icon → "Create Spreadsheet" — this is what becomes your live headcount.
5. Send → the link icon → shorten URL → that's the link to drop in your Instagram bio / DMs / story sticker.

## Form copy (paste in)

**Title:** AFTERIMAGE 001 — RSVP

**Description:**
> Devil's Night. Friday 10.30. Address drops by DM once you're counted.
> Fill this out so we know how many bodies to plan for — that's it, no soul required.

**Question 1** — Short answer, required
> Your name

**Question 2** — Short answer, not required
> Instagram handle (so we can DM you the address)

**Question 3** — Multiple choice or dropdown, required
> How many total, including you?
Options: `1` `2` `3` `4` `5` `6+`
(If `6+`, add a follow-up short-answer question: "How many exactly?" — set it to show only when 6+ is picked, via Section logic, or just leave it as a single dropdown up to 6 and tell big groups to DM you directly.)

## Getting a live headcount number
In the response Sheet, add this formula in any empty cell (adjust the column letter to wherever "How many total" landed, e.g. column C):
```
=SUM(C2:C1000)
```
That's your running total against the 70-pass cap. If you used the `6+` dropdown, treat those as 6 flat (undercounts slightly, which is the safe direction).

## Folding responses into the Pass Tracker
Once the form's live and catching responses, share the response Sheet with me (or just paste me the names) and I'll reconcile new RSVPs against `11 MOTION — Guest List & Pass Tracker.md` — flipping the 30 already-invited names to confirmed when they show up in the form, and adding anyone new who filled it out but wasn't on the original list, so that doc stays the one source of truth doc 00 calls for.

## If you want something slicker instead
Partiful is built exactly for this (RSVP + headcount + the "who's in" social feed) and matches the party-collective vibe better than a bare Google Form, but it's its own account/app — you'd set that up yourself, I can help write the event copy for it if you go that route.
