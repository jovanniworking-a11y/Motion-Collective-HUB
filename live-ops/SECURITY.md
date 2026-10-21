# Security — 21 Oct

Leak check on the files in this drop and the hub clone. No guest list, no API key, and no venue address were in git. Shop addresses in the thrift list are public stores, not the party.

Pipes that were open:

- The counter and the fader listened on every interface with no password. Anyone on the Wi-Fi could read the count or move the master fader.
- Fix: with no MOTION_TOKEN, both bind to 127.0.0.1 only. With MOTION_TOKEN set, they bind to the LAN and the socket must carry `?token=`. The token is an environment variable, never a file in git.
- CHECK IN cannot raise the count while the camera is live.
- RTSP passwords are not printed.

Not fixed here, other seats:

- Cursor: confirm guest_list/ and doc 11 stay gitignored before any push.
- Do not commit a `.env`, a camera URL, or a door recording.

Counts use one shape: occupancy, ins, outs, peak, cap, space_left, ts (UTC, second precision), health.camera is green or red, the other health tiles are green, red, or unknown.

## Attack pass

Tried from the code, not by joining the party Wi-Fi. Cursor, Codex, ChatGPT, and Gemini were not in the room.

- A wrong token, a shortened token, and a `+` turned into a space used to break the check. The compare is now exact.
- The dashboard and the fader page loaded with no token. Both return 401 without it.
- CHECK IN could be hammered past 70. One tap a second, and it stops at cap.
- `NaN`, `Infinity`, or `"mute": "no"` could poison the fader or mute the PA. Those messages are ignored. Anything over 4 KB on the socket is dropped.

Still true: no HTTPS on a house LAN, and the token sits in the iPad URL. Do not screenshot that URL.
