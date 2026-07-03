# EyeBreak

EyeBreak is a small Windows eye-break reminder built with Python, Tkinter, and
`pystray`.

It reminds the user to look far away after a configurable interval, shows a
right-edge auto-hide floating countdown, and provides tray-menu controls for
common actions.

## Current Status

Implemented:

* Right-edge docked auto-hide floating countdown showing time until the next reminder.
* Topmost reminder popup with break countdown.
* Skip, pause, resume, immediate break, and exit flows.
* Mouse-wheel pause-duration adjustment on the reminder popup pause button.
* System tray menu powered by `pystray`.
* Custom EyeBreak icon used by the tray, Tkinter reminder window, and Windows taskbar grouping.
* Tray pause menu with selectable pause durations:

  * 5 minutes;
  * 15 minutes;
  * 30 minutes;
  * 60 minutes;
  * 120 minutes.
* JSON configuration for:

  * reminder interval;
  * break duration;
  * pause duration.

Pending manual acceptance:

* Right-edge docked auto-hide floating countdown display.

Not implemented yet:

* Packaging.
* Startup integration.
* Accounts.
* Cloud sync.
* Daily reports.
* AI analysis.
* Camera detection.
* Full pomodoro behavior.

Manual acceptance status:

* Initial reminder flow accepted by the user.
* Earlier countdown status window accepted by the user before it was replaced by the floating countdown.
* System tray behavior accepted by the user.
* Tray pause-duration selection accepted by the user.
* Program icon implementation accepted by the user, including tray, window,
  and Windows taskbar icon behavior.
* Floating countdown display is implemented but not yet accepted by the user.

## Install

Runtime tray support depends on `pystray` and Pillow.

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run

Run the app:

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

Run automated tests:

```powershell
python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest
```

Last known automated result: `18 passed` with the command above.

Environment note:

* Use `--basetemp=.tmp\pytest` to avoid temp/cache write issues in restricted
  environments.
* In this Windows sandbox, ordinary-permission pytest may fail while cleaning
  `.tmp\pytest` with `PermissionError: [WinError 5]`; the escalated rerun passed.

## Acceptance Checklist

Before a UI milestone is considered accepted, manually verify the relevant flow.

### Floating Countdown

* On startup, only a narrow tab is visible on the right edge of the screen.
* Moving the mouse pointer onto the tab reveals the countdown panel.
* Moving the mouse pointer away hides the panel again after a short delay.
* The countdown panel shows time until the next reminder.
* The countdown text updates once per second.
* During pause, the countdown panel shows remaining pause time in yellow.
* After pause ends, reminders resume and the floating panel shows the next reminder countdown.
* The floating panel stays above normal windows without becoming a full workflow screen.

### Basic Reminder Flow

* Short interval reminder appears when the countdown reaches zero.
* Reminder popup appears centered and topmost.
* Reminder popup countdown decreases once per second.
* Reminder popup closes automatically when countdown reaches zero.
* Skip closes the popup and starts the next reminder interval.
* Exit from the reminder popup terminates the app.

### Pause Flow

* Reminder popup pause button uses the default pause duration from `config.json`.
* Mouse wheel over the pause button adjusts the pause duration between 1 and 120
  minutes before clicking pause.
* Pause closes the popup.
* During pause, the floating countdown panel shows remaining pause time.
* After pause ends, reminders resume and the floating countdown panel shows the
  next reminder countdown.

### Tray Flow

* Tray icon appears in the Windows system tray.
* Tray menu item "立即休息" opens the reminder popup immediately.
* Tray menu item "暂停" opens duration choices:

  * 5 minutes;
  * 15 minutes;
  * 30 minutes;
  * 60 minutes;
  * 120 minutes.
* Choosing each tray pause duration updates the countdown panel to that chosen
  pause length, not the fixed configured default.
* Tray menu item "恢复" clears pause and starts a fresh reminder countdown.
* Tray menu item "退出" terminates the app and removes the tray icon.

### Icon Check

* Tray icon appears correctly in the Windows system tray.
* Reminder popup shows the EyeBreak icon in the title bar.
* Windows taskbar shows the EyeBreak icon instead of the default Python icon when the app is represented there.
* Icon appearance is visually acceptable on Windows.

## Release Discipline

Follow `AGENTS.md` for commit, test, acceptance, and push rules.

Summary:

* Update `README.md` and `HANDOFF.md` before milestone acceptance when behavior,
  commands, dependencies, or acceptance status changes.
* Run relevant tests before committing.
* Report exact test commands and results when reporting completion.
* Do not claim tests passed unless they were actually run.
* Inspect `git status` before committing.
* Exclude unrelated, temporary, local IDE, cache, or scratch files from commits.
* Do not push until the user explicitly confirms acceptance has no issues, such
  as "验收没有问题".
* Push only the accepted milestone to GitHub.

## Next Planned Feature

The right-edge auto-hide floating countdown is implemented and pending manual acceptance.

Possible next refinement after acceptance:

* Tune the hidden tab width or reveal delay if the manual feel is too sensitive or too hard to trigger.

Do not start packaging or startup integration before tray behavior, icon behavior, and floating countdown behavior are stable.