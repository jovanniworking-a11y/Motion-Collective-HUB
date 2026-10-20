# AFTERIMAGE 002: TKE house (UT Austin) backyard, satellite and parcel analysis
Prepared 19 Oct 2026 (America/Chicago). Read-only desk research. Nobody was contacted. **Every area below is an estimate unless it is labelled as a record value.**

## 1. Location
- **Address: 909 W 22nd St, Austin, TX 78705.** This is the Gamma-Upsilon chapter of Tau Kappa Epsilon, founded locally in 1951.
  - Sources: the chapter site (tketexas.com, contact and history pages) and the UT Texas IFC chapter page (texasifc.com/tau-kappa-epsilon). The IFC page lists the current president and the address.
  - OSM/Nominatim check: the address resolves to building way 380917039 at 30.28524, -97.74745, with addr 909 West 22nd Street. OSM height is 10 m.
  - TCAD parcel: City of Austin ArcGIS `EXTERNAL_tcad_parcel` returns PROP_ID 203610, PID 0212010803, situs "909".
- **⚠ Occupancy flag:** this property has been on the Austin MLS for rent since 1 Sep 2026 (MLS 3193694, Metro 512 Realty). The listing is for 12 bedrooms on a 12-month lease. The rent was cut to $17,500/mo on 15 Oct 2026, and the listing is still active.
  - Source: Coldwell Banker, Compass, and Weichert listing pages.
  - This could mean the chapter is leaving, the house is changing hands, or it's just a routine re-lease. Before any planning, confirm with Tea/TKE that the chapter will hold the house on the event date and that the owner allows events.

## 2. Parcel and building (record and map data)
| Item | Value | Source |
|---|---|---|
| Lot, legal | 70.9 ft x 93.8 ft, OLT 25 Division D | TCAD legal description (via HAR/LoopNet) |
| Lot area | 6,726 ft² (0.1544 ac) record; 6,700 ft² from the GIS polygon | TCAD / computed from parcel polygon |
| Building | 2 stories, 4,865 ft² living area, built 1907, 12 bed / 6 bath (listing), wood fence, 6 off-street parking spaces | TCAD/MLS |
| Building footprint | ~2,890 ft² | computed from OSM polygon (vector) |
| Uncovered lot (lot minus footprint) | ~3,800–3,860 ft² | computed |

## 3. Imagery
- Source: Esri World Imagery tiles. Esri's metadata identifies them as **Nearmap Austin, captured 8 Oct 2023**, native 7.5 cm, but served only to zoom 19.
- Ground scale at 30.285°N:
  - z19: **0.258 m/px**. This is the effective resolution.
  - z20: 0.129 m/px. These tiles are upsampled, so they add no detail.
- Parcel and footprint overlays line up with the visible roof and lot edges to within about 1 m.
- Files (all in /workspace/mc-review/tke-backyard/):
  - `tke_backyard_annotated.png`: lot close-up with parcel (yellow), footprint (cyan), rear yard (red), side yards (orange), front strip (blue), detected canopy (green), a 30 ft scale bar, and a north arrow.
  - `tke_lot_raw_z20.png`: the same view without annotations.
  - `tke_context_z19.png`: block context with a 100 ft scale bar.
  - `esri_z19.png`, `esri_z20.png`: the full stitched mosaics.
  - `analyze.py`: the area and mask code. `numbers.json` holds the raw outputs.
  - `EXTERNAL_tcad_parcel.geojson`, `osm_bldg.json`: the source geometries.

## 4. What the imagery shows
**Zones.** Raster areas run about 1.5% above the vector areas.
- **Rear (backyard) yard:** about **70.7 ft wide x ~21 ft deep ≈ 1,450–1,470 ft² gross**. It's measured from the building's rear line to the back property line.
  - In the image it is mostly in shadow (about 70% of pixels are dark) and partly under canopy (about 21% of pixels classed as vegetation).
  - The back line borders a neighbouring flat-roof building directly to the south, so there seems to be **no rear street or alley exit**.
  - East of the yard is the neighbour's paved parking and driveway, presumably behind the fence.
- **Side yards:** about 2,000 ft² gross total.
  - West strip: about 15–19 ft wide x ~70 ft. It's largely under a large tree canopy along the west line, next to a large flat-roof commercial or mechanical building to the west.
  - East strip: about 5–8 ft wide, also under a large tree. In practice it's a walkway, not party space.
- **Front strip:** about 5 ft x 70 ft (~390 ft²) between the building and the W 22nd St sidewalk. Cars park nose-in along the frontage.

**Obstacles and structures visible or likely:**
1. **Large trees:**
   - One large tree on the west side yard, with canopy over most of the west strip and the SW rear corner.
   - One large tree at the east line, with canopy over the east strip and the SE rear corner.
   - Trunk positions can't be seen. Plan for trunks and roots to take floor space.
2. A darker, lower roof or deck section at the rear of the house, included in the OSM footprint. It could be a porch, deck, or addition; it's unclear from the image.
3. A small light object near the SW rear area. It could be stairs, bins, or a small structure; it can't be identified.
4. Wood fence (per the MLS). The fence line follows the parcel edges as far as the image shows.
5. **AC units, trash bins, and utility meters** are typical but can't be seen under the shade.
6. No pool, shed, or large patio is visible. No slope can be read from the imagery; the area is generally flat West Campus, but this is unverified.

## 5. Usable area and capacity
Assumptions:
- Rear-yard usable area = gross minus tree trunks/roots, rear deck or stairs, AC and bins, a DJ and booth footprint (~80–120 ft²), and a clear 44-inch or wider egress path. That gives an estimate of **900–1,200 ft²**.
- All outdoor space usable (rear + west side + front, with egress kept clear, east strip used only as a path, and cars removed): **~2,000–2,800 ft²**.
- Ground-floor indoor space, if opened: 4,865 ft² over two floors is about 2,430 ft² gross per floor. Usable open floor after walls, kitchen, bathrooms, and stairs is an estimate of **~1,200–1,600 ft²**.

| Area | Usable ft² (est.) | @10 ft²/p (comfortable) | @7 ft²/p (MOTION rule) | @5 ft²/p (packed standing) |
|---|---|---|---|---|
| Backyard only | 900–1,200 | 90–120 | 130–170 | 180–240 |
| All outdoor ground | 2,000–2,800 | 200–280 | 285–400 | 400–560* |
| Ground-floor indoor | 1,200–1,600 | 120–160 | 170–230 | 240–320 |
| Outdoor + indoor | 3,200–4,400 | 320–440 | 455–630 | 640–880* |

\*Packed densities across narrow side strips and a sidewalk-facing front strip aren't realistic, and egress would fail. Treat these as theoretical ceilings only.

**Against the stated 450:**
- The backyard alone holds roughly **90–170 people at once**, which is about 20–40% of 450.
- To hold 450 at the same time at the 7 ft²/person rule, you need about **3,150 ft² of clear usable floor**. That's about 2.5–3.5x what the backyard has.
- Even the whole lot's uncovered ground (~3,800 ft² gross, ~2,000–2,800 usable) reaches 450 only at packed density.
- **So 450 simultaneous guests needs the house interior plus all yards.** Even then, MOTION's own 7 ft² rule gives roughly 455–630 only at the optimistic end, with egress limited to the 22nd St frontage.
- A realistic plan is either a **150–250 simultaneous cap with door-controlled turnover**, which could total around 400 over the night, or a larger venue.
- Building-code reference point: the IBC occupant-load factor for assembly standing space is 5 net ft²/person. The 7 ft² figure matches "concentrated, chairs only." Code load is a ceiling, not a comfort target. The fire marshal's number governs.

## 6. Limits
- Effective resolution is about 0.26 m/px, so objects under about 0.5 m (AC pads, bins, steps, small stairs) aren't reliable.
- The imagery is from **Oct 2023**, three years old. Trees, decks, fences, and parking may have changed.
- Canopy and shadow hide about 65% of the uncovered ground. The surface (grass, gravel, pavers, dirt), trunk positions, and anything under the trees are unknown.
- The fence position and any gates can't be confirmed. The parcel line is not the same as the fence line.
- There's no elevation data at this scale, so slope and steps can't be seen.
- The OSM footprint is hand-traced. The rear section's use (deck vs. enclosed room) is uncertain.
- Usable-area deductions are judgment estimates and are given as ranges.

## 7. Ground-visit checklist
1. Tape or laser-measure the rear yard, both side yards, and the front strip. Mark tree trunks, deck, stairs, AC units, meters, and bins.
2. Map gates and **egress routes**: how many exits lead to a public way, their widths, and whether anything opens to the neighbouring lots. Confirm there's no rear exit.
3. Ground surface and slope, lighting, and trip hazards. Branch clearance for any tent, truss, or 360-camera rig.
4. Which interior rooms the chapter will open, their measurements, the stair condition, and how many restrooms. Plan portable toilets for crowds over 100.
5. Power: circuit capacity and outlet locations for the DJ, lights, and cameras. Whether a generator is needed.
6. Entry control: wristbands and ID check at the 22nd St frontage. Queue space on the sidewalk without blocking it.
7. Neighbours: dense apartments on all sides. Check noise exposure, Austin's sound ordinance limits and hours, and the neighbour notification plan.
8. Permits and approvals to confirm (not verified here):
   - The owner's or landlord's written OK, given the MLS listing.
   - UT IFC / Fraternity & Sorority Life event-registration and risk rules for chapter-facility events.
   - City of Austin special-event or amplified-sound permits through the Austin Center for Events.
   - Fire marshal occupancy guidance.
   - TABC rules if alcohol is sold or entry is charged.
9. Parking and rideshare pickup on W 22nd St, and emergency vehicle access.
10. Confirm the house is still TKE-occupied on the event date (see §1).
