# Reminders · 75 XP
No-shows cost the clinic money. A text the day before cuts them a lot.

Write in `quest.py`:
1. `reminder_text(patient, appt)` → exactly:
   `"Hi Jane, this is Dr. Kim's Clinic reminding you of your appointment on Wed 21 Oct at 2:30 PM. Reply C to confirm or X to cancel."`
   (hour without a leading zero, 12-hour clock with AM/PM).
2. `who_to_remind(appts, now)`: the ids (sorted) of appointments starting between 23 and 25 hours after `now`.

Never put medical details (reason for visit, diagnosis) in a text message: only name, date and time.

<details><summary>Hint</summary>

`start.strftime("%a %d %b")` → `"Wed 21 Oct"`. For the hour: `start.strftime("%I:%M %p").lstrip("0")`.
</details>
