# learn/ · coding for MOTION

Three tracks. Each exercise is a small piece of a real MOTION job: you fill in `exercise.py`, then run the check.

```bash
pip install numpy pillow          # once
python learn/check.py py01        # check one exercise
python learn/check.py all         # see where you are
```

A check prints PASS or tells you exactly what's wrong. Hints are in each exercise's `README.md`. Try for 20 minutes before reading a hint, and ask Claude to *explain* an error, not to fix it.

**Data rule:** the exercises use made-up data only (Guest 01, Guest 02, …). Real guest lists never go in git.

## Track 1 · Python on MOTION work (with CS50P + Automate the Boring Stuff)
| # | Exercise | You learn | Do it after |
|---|---|---|---|
| py01 | Rename a folder of clips to `2026-10-30_iamariology_01.mp4` | strings, f-strings, loops, files | CS50P weeks 0–2 |
| py02 | Budget: totals and the buffer, with confirmed/estimate labels | lists, dicts, functions | CS50P week 3 |
| py03 | RSVP export → heads per day | reading CSV, counting | CS50P week 6 |
| py04 | Beat grid: when does every cut land? | maths, rounding, the music logic of our edits | any time |
| py05 | B&W with a colour filter, like the reels | images as arrays (Pillow + NumPy) | Automate ch. 19 |
| py06 | Read `hub.py` and add one field | reading real code | after py01–py05 |

## Track 2 · Machine learning (with Kaggle Learn, then fast.ai)
| # | Exercise | You learn |
|---|---|---|
| ml01 | Predict turnout from RSVPs (a straight-line fit, built from scratch) | what "training" and "error" mean |
| ml02 | Tell sharp frames from blurry ones (pick the best freeze frame) | features, thresholds, accuracy |
| ml03 | Group clips by look (k-means, from scratch) | unsupervised learning |

Courses, in order (all free):
1. **Kaggle Learn: Intro to Machine Learning**, then **Intermediate ML** (kaggle.com/learn). Hands-on, a few hours each.
2. **3Blue1Brown, "Neural networks"** video series on YouTube. The intuition, with no maths homework.
3. **fast.ai, Practical Deep Learning for Coders** (course.fast.ai). You train real image models in lesson 1. The best next step.
4. **Andrew Ng, Machine Learning Specialization** (Coursera, free to audit). The theory, once you want it.
5. **Hugging Face Course** (huggingface.co/learn). Using ready-made AI models (text, audio, images) in your own code.

## Track 3 · Using Claude Code, Codex and AI to their full potential
| # | Exercise | You learn |
|---|---|---|
| ai01 | Write a real task brief and hand it to Claude Code | asking for exactly what you want |
| ai02 | Turn one of your rules into a skill | making the AI remember how you work |
| ai03 | The review loop: read the diff, ask "why", catch a mistake | staying the director |

Reading (free):
- **Anthropic's prompt engineering tutorial**: github.com/anthropics/courses (interactive notebooks).
- **Claude Code docs**: code.claude.com/docs. Read *CLAUDE.md*, *Skills*, *Hooks* and *Common workflows*.
- **OpenAI Codex docs**: developers.openai.com/codex, for the PC-side jobs we route to Codex.

## Pace
30–60 minutes a day. About one Python exercise a week alongside CS50P; ML from week 6; the AI track any time, because it pays off immediately.
