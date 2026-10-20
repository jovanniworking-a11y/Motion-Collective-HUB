# Night-Of Ops (crew phones)

Offline-capable local page for **Devil's Night · AFTERIMAGE 001** (Fri 30 Oct 2026).

**Draft only — do not publish.** Hosting stays with Jovanni.

## Run locally

```bash
# from repo root
python3 -m http.server 8765 --directory ops
# open http://localhost:8765/
```

On first load (online), the service worker caches the shell. Check-ins and welfare logs live in `localStorage` on that device (`motion-night-ops-v1`). No guest names, no venue address.

## Tabs
1. **Door** — passes 001–050 (working cap, estimate); tap to check in; live count vs cap.
2. **Show** — crew run-of-show with countdowns; current block highlighted.
3. **Welfare** — 30-minute rounds doors→hard stop; log per round; 12:30 collision alert.
4. **Budget** — pool $450 (confirmed), spend $381.13 (estimate), buffer $68.87 (estimate).

Use **Clock → Jump to event night** to rehearse before Oct 30.
