"""Builds the MOTION artist brief (teaser-poster direction) as HTML; Chrome prints it to PDF."""
import json, html, sys, os
D = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(f"{D}/music.json", encoding="utf-8"))
NAME = sys.argv[1] if len(sys.argv) > 1 else "iamariology b2b raymixes"
e = html.escape
MARK = '<span class="mmmm"><span>M</span><span>M</span><span>M</span><span>M</span></span>'

CSS = r"""
@font-face { font-family: "Bodoni Moda"; src: url("fonts/fontsource-variable-bodoni-moda-5.1.0/package/files/bodoni-moda-latin-wght-normal.woff2") format("woff2"); font-weight: 400 900; }
@font-face { font-family: "Bodoni Moda"; src: url("fonts/fontsource-variable-bodoni-moda-5.1.0/package/files/bodoni-moda-latin-wght-italic.woff2") format("woff2"); font-style: italic; font-weight: 400 900; }
@font-face { font-family: "Jost"; src: url("fonts/fontsource-variable-jost-5.1.0/package/files/jost-latin-wght-normal.woff2") format("woff2"); font-weight: 100 900; }
@font-face { font-family: "JetBrains Mono"; src: url("fonts/fontsource-variable-jetbrains-mono-5.1.0/package/files/jetbrains-mono-latin-wght-normal.woff2") format("woff2"); font-weight: 100 800; }
/* Teaser-poster direction: violet-navy void, steel-blue eyes, upright Bodoni numerals, centred, quiet.
   Red lives only in the MMMM trail. */
:root { --void:#0a0911; --void2:#120f1a; --panel:#15121e; --bone:#ede7db; --dim:#8c8794; --ice:#bcd3e6; --steel:#5f7a96; --line:rgba(237,231,219,.12);
  --m1:#5a1f27; --m2:#7a2a33; --m3:#9b3640; --m4:#ede7db; }
@page { size: 1280px 720px; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; background: var(--void); color: var(--bone); font: 400 18px/1.45 "Jost", sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
a { color: inherit; text-decoration: none; }
.slide { width: 1280px; height: 720px; position: relative; overflow: hidden; break-after: page; padding: 56px 80px; display: flex; flex-direction: column;
  background: radial-gradient(ellipse 70% 75% at 50% 45%, #1a1626 0%, var(--void2) 45%, var(--void) 100%); }
.slide:last-child { break-after: auto; }
.slide::after { content: ""; position: absolute; inset: 0; pointer-events: none; opacity: .07; mix-blend-mode: screen;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }
.mmmm { font-family: "Bodoni Moda"; font-weight: 400; line-height: 1; display: inline-flex; }
.mmmm span { margin-right: -.36em; } .mmmm span:nth-child(1){color:var(--m1)} .mmmm span:nth-child(2){color:var(--m2)} .mmmm span:nth-child(3){color:var(--m3)} .mmmm span:nth-child(4){color:var(--m4);margin-right:0}
.caps { font: 500 12px "Jost"; letter-spacing: .42em; text-transform: uppercase; }
.top { display: flex; justify-content: space-between; color: var(--dim); }
.foot { margin-top: auto; display: flex; justify-content: space-between; font: 400 12px "JetBrains Mono"; color: var(--dim); letter-spacing: .06em; }
h2 { font-family: "Bodoni Moda"; font-weight: 400; font-size: 60px; line-height: 1.04; margin: 0 0 26px; letter-spacing: -.005em; }
h2 i { color: var(--ice); }
.kicker { color: var(--dim); margin: 0 0 16px; }
.center { align-items: center; justify-content: center; text-align: center; }
.mono { font-family: "JetBrains Mono", monospace; font-variant-numeric: tabular-nums; }
.dim { color: var(--dim); }
.hair { width: 56px; height: 1px; background: var(--bone); opacity: .6; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 56px; }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; }
.stat b { display: block; font: 400 72px/1 "Bodoni Moda"; color: var(--bone); }
.stat span { color: var(--ice); }
.stat p { margin: 10px 0 0; color: var(--dim); font-size: 15px; }
.list { margin: 0; padding: 0; list-style: none; display: grid; gap: 13px; }
.list li { display: grid; grid-template-columns: 30px 1fr; gap: 10px; font-size: 18px; }
.list li::before { content: attr(data-n); font: 400 13px "JetBrains Mono"; color: var(--ice); padding-top: 4px; }
.tag { display: inline-block; font: 500 10px "JetBrains Mono"; letter-spacing: .16em; text-transform: uppercase; border: 1px solid var(--line); padding: 3px 8px; color: var(--dim); vertical-align: 2px; }
.u { border-bottom: 1px solid var(--steel); }

/* eyes: cover + statement slides, exactly like the teaser */
.eyes { padding: 0; }
.eyes .strips { position: absolute; inset: 0; display: grid; grid-template-rows: repeat(3, 1fr); gap: 5px; background: #05040a; }
.eyes .strip { background: url("../media/dates_feed.jpg") no-repeat; background-size: 100% 300%; position: relative; display: grid; place-items: center; }
.eyes .strip:nth-child(1){background-position:50% 0} .eyes .strip:nth-child(2){background-position:50% 50%} .eyes .strip:nth-child(3){background-position:50% 100%}
.eyes .strip.clean { background-image: url("../media/eyes_feed.jpg"); }
.eyes .strip::before { content: ""; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(10,9,17,.35), transparent 30%, transparent 70%, rgba(10,9,17,.35)); }
.eyes .strip > * { position: relative; }
.eyes .num { font: 400 64px/1 "Bodoni Moda"; color: var(--bone); text-shadow: 0 2px 30px rgba(0,0,0,.6); }
.eyes .label { position: absolute; left: 80px; top: 34px; z-index: 2; }
.eyes .brand { position: absolute; right: 80px; bottom: 44px; z-index: 2; display: grid; justify-items: center; gap: 8px; }
.eyes .brand .caps { font-size: 13px; }

/* timeline */
.tl { display: grid; grid-template-columns: repeat(12, 1fr); margin-top: 6px; }
.tl .c { border-left: 1px solid var(--line); padding: 10px 8px 0; min-height: 250px; }
.tl .c .t { font: 400 13px "JetBrains Mono"; color: var(--dim); }
.tl .c .m { font-size: 14px; margin-top: 6px; line-height: 1.25; }
.tl .c.you { background: linear-gradient(180deg, rgba(188,211,230,.14), transparent 80%); border-left: 1px solid var(--ice); }
.tl .c.you .t { color: var(--ice); } .tl .c.you .m { font-weight: 500; }
.bar { display: grid; grid-template-columns: 2fr 1.25fr 1.75fr; gap: 4px; margin-top: 16px; font: 500 12px "Jost"; letter-spacing: .2em; text-transform: uppercase; }
.bar div { padding: 14px 16px; background: var(--panel); border-top: 1px solid var(--line); }
.bar .y { border-top-color: var(--ice); color: var(--ice); }

/* music */
.sec { border-top: 1px solid var(--line); padding-top: 12px; }
.sec h3 { margin: 0 0 8px; font: 500 13px "Jost"; letter-spacing: .2em; text-transform: uppercase; display: flex; justify-content: space-between; }
.sec h3 span { font: 400 13px "JetBrains Mono"; color: var(--dim); letter-spacing: 0; }
.trk { display: flex; justify-content: space-between; gap: 12px; font-size: 14px; padding: 3px 0; }
.trk .a { color: var(--dim); } .trk .k { font: 400 12px "JetBrains Mono"; color: var(--ice); white-space: nowrap; }
.sets { display: grid; grid-template-columns: 1fr 1fr; gap: 0 48px; }
.sets a { padding: 14px 0; border-bottom: 1px solid var(--line); font-size: 19px; display: flex; gap: 16px; align-items: baseline; }
.sets a span { font: 400 13px "JetBrains Mono"; color: var(--ice); }
.sets a em { margin-left: auto; font: 400 11px "JetBrains Mono"; color: var(--dim); font-style: normal; }
.plan { width: 100%; border: 1px solid var(--line); }
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.card { border: 1px solid var(--line); padding: 20px; background: rgba(21,18,30,.7); display: flex; flex-direction: column; gap: 8px; min-height: 168px; }
.card h4 { margin: 0; font: 500 15px "Jost"; letter-spacing: .2em; text-transform: uppercase; }
.card p { margin: 0; color: var(--dim); font-size: 15px; }
.card .l { margin-top: auto; font: 400 12px "JetBrains Mono"; color: var(--ice); word-break: break-all; }

/* track index */
.idx { columns: 3; column-gap: 34px; font-size: 11.5px; line-height: 1.35; }
.idx h5 { break-after: avoid; margin: 0 0 4px; padding-top: 6px; font: 500 10.5px "Jost"; letter-spacing: .22em; text-transform: uppercase; color: var(--ice); }
.idx .r { break-inside: avoid; display: grid; grid-template-columns: 1fr auto; gap: 2px 8px; padding: 3px 0; border-bottom: 1px solid rgba(237,231,219,.06); }
.idx .r b { font-weight: 500; } .idx .r .a { color: var(--dim); }
.idx .r .lk { white-space: nowrap; font: 400 10px "JetBrains Mono"; color: var(--dim); }
.idx .r .lk a { color: var(--ice); border-bottom: 1px solid rgba(188,211,230,.35); }
"""

def top(left, right):
    return f'<div class="top caps"><span>{left}</span><span>{right}</span></div>'

def foot(left, n):
    return f'<div class="foot"><span>{left}</span><span>{n:02d}</span></div>'

T = M["tracks"]
def sec(name, n=4):
    rows = [t for t in T if t["sec"] == name]
    items = "".join(f'<div class="trk"><span>{e(t["title"].split(" (")[0])} <span class="a">· {e(t["artist"])}</span></span><span class="k">{e(t["bpm"])} · {e(t["key"])}</span></div>' for t in rows[:n])
    return f'<div class="sec"><h3>{e(name)} <span>{len(rows)}</span></h3>{items}</div>'

slides = []
# 1 cover — the teaser poster, with the night written across the eyes
slides.append(f'''<section class="slide eyes"><div class="strips">
  <div class="strip clean"><span class="num">10.30.26</span></div>
  <div class="strip clean"><span class="num" style="font-style:italic">Devil's Night</span></div>
  <div class="strip clean"><span class="num" style="font-size:40px;font-family:Jost;font-weight:500;letter-spacing:.14em;text-transform:uppercase">{e(NAME)}</span></div></div>
  <div class="label caps dim" style="color:var(--bone)">Artist brief · AFTERIMAGE 001</div>
  <div class="brand">{MARK.replace('class="mmmm"','class="mmmm" style="font-size:44px"')}<span class="caps">MOTION</span></div></section>''')
# 2 difference
slides.append(f'''<section class="slide">{top("Why MOTION","AFTERIMAGE 001")}
  <div style="margin-top:44px"><p class="kicker caps">What makes us different</p>
  <h2>We do everything to the tee.<br>Then we <i>simulate</i> it.</h2>
  <p class="dim" style="max-width:62ch;font-size:19px;margin:0">Before anyone walks in, we've already run the night: the room at real size, a 50-person crowd, the drink line, the bathroom queue, where the jams happen. Every number we plan with is labelled confirmed, estimate or open.</p></div>
  <div class="grid3" style="margin-top:46px">
    <div class="stat"><b>768</b><span class="caps">layouts simulated</span><p>To find a booth where people can stand behind you, Boiler Room style.</p></div>
    <div class="stat"><b>12</b><span class="caps">crowds per finalist</span><p>Every top layout re-run with fresh crowds, so the answer isn't luck.</p></div>
    <div class="stat"><b>12:00</b><span class="caps">the peak, designed</span><p>Ice on the walls, warm on faces, then red at midnight. No haze, no lasers.</p></div></div>
  {foot("Mission: show off the artists. Put them in front of a room that's ready for them.",2)}</section>''')
# 3 the night
tl = [("6:00","Load-in, room reset",0),("7:00","System build + cable check (iamariology helps)",1),("7:45","Sound check",1),("8:30","Crew briefing",0),("9:00","Doors · your opening set",1),("11:00","Glamz (solo)",0),("12:00","Peak cue: red light, eyes on",0),("12:15","HE//THEY",0),("12:30","Last entry",0),("1:30","Best costume ($40)",0),("1:45","Last pour",0),("2:00","Last song · hard stop",0)]
cells = "".join(f'<div class="c{" you" if y else ""}"><div class="t">{t}</div><div class="m">{e(m)}</div></div>' for t,m,y in tl)
slides.append(f'''<section class="slide">{top("The night","Friday 10.30")}
  <p class="kicker caps" style="margin-top:36px">Run of show · confirmed</p><h2 style="margin-bottom:14px">You open the room.</h2>
  <div class="tl">{cells}</div>
  <div class="bar"><div class="y">9:00–11:00 · {e(NAME)}</div><div>11:00–12:15 · Glamz</div><div>12:15–2:00 · HE//THEY · co.b b2b NiiON</div></div>
  {foot("Doors 9 PM · 21+ · invite only, numbered passes · cap 50",3)}</section>''')
# 4 your set
slides.append(f'''<section class="slide">{top("Your set","9:00 – 11:00 PM")}
  <div class="grid2" style="margin-top:44px;align-items:start"><div><p class="kicker caps">The brief</p><h2>Build it.<br><i>Don't peak it.</i></h2>
  <p class="dim" style="margin:0;font-size:18px">You're the first thing people hear. Take the room from people arriving with a drink to a full floor, then hand a warm room to Glamz at 11, who takes it on to HE//THEY.</p></div>
  <ul class="list" style="margin-top:46px">
   <li data-n="01"><span><b>9:00–10:00</b> · arrivals. Groove first, room to talk. <span class="tag">suggestion</span></span></li>
   <li data-n="02"><span><b>10:00–11:00</b> · the floor fills. Lift toward garage and house.</span></li>
   <li data-n="03"><span><b>11:00</b> · hand off to Glamz, who plays solo until 12:15. Let's agree where you finish (BPM, key) so the handoff is clean.</span></li>
   <li data-n="04"><span><b>12:00</b> · the designed peak lands in Glamz's set: lights go red, the eyes come on.</span></li>
   <li data-n="05"><span><b>12:15</b> · HE//THEY closes: UKG, hard house / electro, bass house, mostly <span class="mono">134–140</span> BPM. That's where the night is heading.</span></li></ul></div>
  {foot("Timings and handoffs are ours to agree together. Nothing here is a set list.",4)}</section>''')
# 5 sound
slides.append(f'''<section class="slide">{top("The sound","Songs We Love · inspiration only")}
  <p class="kicker caps" style="margin-top:32px">What the room loves · BPM · key (Camelot)</p><h2 style="font-size:48px;margin-bottom:18px">The taste, <i>not the tracklist.</i></h2>
  <div class="grid3">{sec("UKG, 2-step & speed garage")}{sec("Bass, electro & breaks")}{sec("Rave & trance")}</div>
  <p class="dim" style="margin:22px 0 0;font-size:16px">Plus deep dives on Silva Bumpa, Interplanetary Criminal, KETTAMA, Prospa and camoufly, and 19 UKG, garage + house classics. <b style="color:var(--bone)">Every track, with YouTube Music and SoundCloud links, is at the back of this brief</b> · full sheet: <a class="u" href="https://docs.google.com/spreadsheets/d/1eKUQ-AdmoJxPCy6ff1mUEMih1-o_ZOVz1BjB-vul4Ho/edit">Songs We Love</a></p>
  {foot(f"{len(T)} tracks · built from what our guests and crew play, save and sing",5)}</section>''')
# 6 sets
sl = "".join(f'<a href="{e(s["url"])}"><span>{i+1:02d}</span>{e(s["name"].replace(" — "," · ").replace("Boiler Room: ","Boiler Room "))}<em>watch ↗</em></a>' for i,s in enumerate(M["sets"]))
slides.append(f'''<section class="slide">{top("Sets we love","the energy we're after")}
  <p class="kicker caps" style="margin-top:40px">Watch before the 30th · tap to open</p><h2>The room we're building.</h2>
  <div class="sets">{sl}</div>{foot("Each title links to the full set",6)}</section>''')
# 7 eyes statement — teaser interlude
slides.append(f'''<section class="slide eyes"><div class="strips">
  <div class="strip clean"><span class="num" style="font-size:44px">Ice on the walls.</span></div>
  <div class="strip clean"><span class="num" style="font-size:44px">Warm on the faces.</span></div>
  <div class="strip clean"><span class="num" style="font-size:44px;font-style:italic">Red at midnight.</span></div></div>
  <div class="label caps" style="color:var(--bone)">The light</div><div class="brand">{MARK.replace('class="mmmm"','class="mmmm" style="font-size:38px"')}</div></section>''')
# 8 room
slides.append(f'''<section class="slide">{top("The room","simulated 16 Oct · 50 guests")}
  <div style="display:grid;grid-template-columns:1fr 320px;gap:36px;margin-top:28px;flex:1;min-height:0">
   <div style="display:flex;align-items:center"><img class="plan" src="../sim/compare.png" alt="Top view of both layouts"></div>
   <div><p class="kicker caps">Our pick</p><h2 style="font-size:42px">A row of people <i>behind you.</i></h2>
    <ul class="list" style="font-size:16px">
     <li data-n="01"><span>Table 2 ft off the wall, so one row stands behind the DJ. The Boiler Room shot.</span></li>
     <li data-n="02"><span>Speakers on tripods beside the table, facing the floor.</span></li>
     <li data-n="03"><span>Crowd score <span class="mono">27.9</span> vs <span class="mono">30.2</span> on the wall: fewer jams. <span class="tag">sim</span></span></li>
     <li data-n="04"><span>Door path unchanged. Confirmed after today's measurements.</span></li></ul></div></div>
  {foot("Left: decks on the wall · Right: the 360 cut (red = people behind the DJ)",8)}</section>''')
# 9 booth
slides.append(f'''<section class="slide">{top("The booth","gear + light")}
  <p class="kicker caps" style="margin-top:40px">What you'll play on</p><h2>Club standard, <i>in a living room.</i></h2>
  <div class="grid2"><ul class="list">
   <li data-n="01"><span><b>2× Pioneer CDJ-2000NXS2</b> + <b>DJM-900NXS2</b>, rented <span class="tag">confirmed</span></span></li>
   <li data-n="02"><span>48 × 24 in table at 40 in · 36 in DJ zone · 24 in no-drinks strip</span></li>
   <li data-n="03"><span>PA + lights from Rapid Ric · booth monitor requested <span class="tag">open</span></span></li>
   <li data-n="04"><span>Bring rekordbox USBs and a backup stick</span></li></ul>
  <ul class="list">
   <li data-n="05"><span>Ice wash, warm red/amber on faces, mirror ball, red at midnight</span></li>
   <li data-n="06"><span>No haze, no fog, no lasers (smoke detectors)</span></li>
   <li data-n="07"><span>Kept near <span class="mono">80 dB</span> for the neighbours · sub off the shared wall</span></li>
   <li data-n="08"><span>Phones down on the floor · one camera · a lit photo corner</span></li></ul></div>
  {foot("Sound check 7:45 PM · one person owns the master fader all night",9)}</section>''')
# 10 built
slides.append(f'''<section class="slide">{top("What we built","the MOTION system")}
  <p class="kicker caps" style="margin-top:40px">Tools behind the night</p><h2 style="margin-bottom:22px">Planned like a tour. <i>Run like a club.</i></h2>
  <div class="cards">
   <div class="card"><h4>Room Studio</h4><p>The apartment in 3D at real size. Drag gear, rank drink spots, watch a full night of crowd flow.</p><a class="l" href="https://claude.ai/artifact/49y1uMCWh1em8QAfMbvBiV">claude.ai/artifact/49y1uMCWh1em8QAfMbvBiV</a></div>
   <div class="card"><h4>MOTION site</h4><p>Lineup, countdown, the format, floor policy and RSVP. Where fans find the next night.</p><a class="l" href="https://claude.ai/artifact/Fjd1GpHBNFyu21EJtNBCgB">claude.ai/artifact/Fjd1GpHBNFyu21EJtNBCgB</a></div>
   <div class="card"><h4>RSVP</h4><p>Every guest gets counted and a numbered pass. The address goes by DM, never public.</p><a class="l" href="https://tally.so/r/Ekj7zA">tally.so/r/Ekj7zA</a></div>
   <div class="card"><h4>Collective Hub</h4><p>Tasks, run of show, crew roles, budget and a Tonight view, live from our planning sheet.</p><span class="l">crew only</span></div>
   <div class="card"><h4>Event learning</h4><p>Plan vs actual after every night: headcount, drinks, lines, sound. The next one gets better.</p><span class="l">crew only</span></div>
   <div class="card"><h4>Instagram</h4><p>Teasers, the lineup reveal, the reel. Your clips go here with your OK.</p><a class="l" href="https://instagram.com/motioncollective.atx">@motioncollective.atx</a></div></div>
  {foot("Everything above is built and running for AFTERIMAGE 001",10)}</section>''')
# 11 need
slides.append(f'''<section class="slide">{top("What we need from you","before the 30th")}
  <p class="kicker caps" style="margin-top:40px">Five quick things</p><h2>Your part.</h2>
  <div class="grid2"><ul class="list">
   <li data-n="01"><span><b>Credit:</b> exact spelling of both names, and OK to be on the flyer, reel, IG and site</span></li>
   <li data-n="02"><span><b>Clips:</b> 30–60 s of audio with the drop time, a short video of you playing, OK to post</span></li>
   <li data-n="03"><span><b>Handles</b> for tags</span></li></ul>
  <ul class="list">
   <li data-n="04"><span><b>Gear:</b> what you're bringing (surge protector?), USB format, headphones or monitor</span></li>
   <li data-n="05"><span><b>Plus-ones</b> (we're capped at 50) and agreeing your fee, in writing</span></li></ul></div>
  {foot("Questions any time: DM @motioncollective.atx",11)}</section>''')
# 12 close — the logo post
slides.append(f'''<section class="slide center">{MARK.replace('class="mmmm"','class="mmmm" style="font-size:190px"')}
  <div class="caps" style="font-size:20px;margin-top:34px">MOTION</div><div class="caps dim" style="font-size:12px;margin-top:12px">Austin</div>
  <div class="hair" style="margin:34px 0 22px"></div><h2 style="font-size:40px;margin:0">See you <span class="mono" style="font-family:'Bodoni Moda'">10.30.26</span></h2>
  <p class="dim" style="margin-top:14px">Track list with links follows.</p></section>''')
# 13+ track index, every track with YouTube Music + SoundCloud links
order = []
for t in T:
    if t["sec"] not in order: order.append(t["sec"])
blocks = []
for s in order:
    rows = "".join(f'<div class="r"><span><b>{e(t["title"])}</b> <span class="a">· {e(t["artist"])}</span></span><span class="lk">{(e(t["bpm"])+" · "+e(t["key"])+" · ") if t["bpm"] else ""}<a href="{e(t["yt"])}">YT</a> <a href="{e(t["sc"])}">SC</a></span></div>' for t in T if t["sec"] == s)
    blocks.append(f'<h5>{e(s)}</h5>{rows}')
per = [0]
# split sections across pages by row count (≈ 3 columns × 34 rows per page)
pages, cur, n = [], [], 0
for s, b in zip(order, blocks):
    c = sum(1 for t in T if t["sec"] == s) + 2
    if cur and n + c > 96: pages.append(cur); cur, n = [], 0
    cur.append(b); n += c
if cur: pages.append(cur)
for i, p in enumerate(pages):
    slides.append(f'''<section class="slide" style="padding:46px 64px 40px">{top("Songs We Love · every track",f"index {i+1}/{len(pages)}")}
      <p class="dim" style="margin:14px 0 14px;font-size:13px">Tap <b style="color:var(--ice)">YT</b> to open in YouTube Music, <b style="color:var(--ice)">SC</b> for SoundCloud. Inspiration only, not a set list.</p>
      <div class="idx">{"".join(p)}</div>{foot("MOTION Collective · AFTERIMAGE 001",13+i)}</section>''')

open(f"{D}/deck2.html", "w", encoding="utf-8").write(
  f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>MOTION · Devil\'s Night · Artist Brief</title><style>{CSS}</style></head><body>{"".join(slides)}</body></html>')
print(len(slides), "slides;", len(pages), "index pages")
