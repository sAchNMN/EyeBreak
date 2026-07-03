# EyeBreak

EyeBreak is a small Windows eye-break reminder built with Python and Tkinter.
It reminds the user to look far away after a configurable interval, shows a
countdown status window, and provides tray-menu controls for common actions.

## Current Status

Implemented:

- Countdown status window showing time until the next reminder.
- Topmost reminder popup with break countdown.
- Skip, pause, resume, immediate break, and exit flows.
- Mouse-wheel pause-duration adjustment on the reminder popup pause button.
- System tray menu powered by `pystray`.
- JSON configuration for reminder interval, break duration, and pause duration.

Manual acceptance status:

- Initial reminder flow accepted by the user.
- Countdown status window accepted by the user.
- System tray behavior accepted by the user.

## Install

```powershell
python -m pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

For faster acceptance testing, temporarily set `config.json` to short intervals:

```json
{
  "reminder_interval_minutes": 0.1667,
  "break_duration_seconds": 10,
  "pause_minutes": 1
}
```

Restore normal values after testing:

```json
{
  "reminder_interval_minutes": 25,
  "break_duration_seconds": 20,
  "pause_minutes": 60
}
```

## Test

```powershell
python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest
```

Last known automated result: `6 passed`.

## Acceptance Checklist

Before a feature is considered accepted, manually verify the relevant UI flow.
For the current tray milestone, verify:

- Tray icon appears in the Windows system tray.
- `立即休息` opens the reminder popup immediately.
- `暂停` pauses using the configured `pause_minutes`.
- `恢复` clears pause and starts a fresh reminder countdown.
- `退出` terminates the app and removes the tray icon.

## Release Discipline

At each key development milestone:

1. Update this README with current behavior, run/test instructions, and manual
   acceptance status.
2. Update `HANDOFF.md` with implementation details and next work.
3. Run the relevant tests.
4. Local commits are allowed at development milestones after README and handoff
   updates are written and relevant tests pass.
5. Do not push until the user explicitly says acceptance has no issues.
6. After the user says acceptance has no issues, push the accepted milestone to
   GitHub.
