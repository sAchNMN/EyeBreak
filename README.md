# EyeBreak

EyeBreak is a small Windows eye-break reminder built with Python, Tkinter, and
`pystray`.

It reminds the user to look far away after a configurable interval, shows a
countdown status window, and provides tray-menu controls for common actions.

## Current Status

Implemented:

* Countdown status window showing time until the next reminder.
* Topmost reminder popup with break countdown.
* Skip, pause, resume, immediate break, and exit flows.
* Mouse-wheel pause-duration adjustment on the reminder popup pause button.
* System tray menu powered by `pystray`.
* Custom EyeBreak icon used by the tray and Tkinter windows.
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

Not implemented yet:

* Edge-docked auto-hide floating countdown display.
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
* Countdown status window accepted by the user.
* System tray behavior accepted by the user.
* Tray pause-duration selection accepted by the user.
* Program icon implementation is automated-test covered, but visual UI
  acceptance on Windows is still pending.

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

Last known automated result: `11 passed` with the command above.

Environment note:

* Use `--basetemp=.tmp\pytest` to avoid temp/cache write issues in restricted
  environments.

## Acceptance Checklist

Before a UI milestone is considered accepted, manually verify the relevant flow.

### Basic Reminder Flow

* Short interval reminder appears when the countdown reaches zero.
* Reminder popup appears centered and topmost.
* Reminder popup countdown decreases once per second.
* Reminder popup closes automatically when countdown reaches zero.
* Skip closes the popup and starts the next reminder interval.
* Exit from the reminder popup terminates the app.

### Countdown Status Window

* Countdown status window appears on startup.
* Countdown status window shows time until the next reminder.
* Countdown status window updates once per second.
* Countdown status window stays visible above normal windows.
* Exit from the countdown status window terminates the app.

### Pause Flow

* Reminder popup pause button uses the default pause duration from `config.json`.
* Mouse wheel over the pause button adjusts the pause duration between 1 and 120
  minutes before clicking pause.
* Pause closes the popup.
* During pause, the countdown status window shows remaining pause time.
* After pause ends, reminders resume and the status window shows the next
  reminder countdown.

### Tray Flow

* Tray icon appears in the Windows system tray.
* Tray menu item "立即休息" opens the reminder popup immediately.
* Tray menu item "暂停" opens duration choices:

  * 5 minutes;
  * 15 minutes;
  * 30 minutes;
  * 60 minutes;
  * 120 minutes.
* Choosing each tray pause duration updates the countdown window to that chosen
  pause length, not the fixed configured default.
* Tray menu item "恢复" clears pause and starts a fresh reminder countdown.
* Tray menu item "退出" terminates the app and removes the tray icon.

### Icon Check

* Tray icon appears correctly in the Windows system tray.
* Countdown status window shows the EyeBreak icon in the title bar.
* Reminder popup shows the EyeBreak icon in the title bar.
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

Planned user-requested feature:

* Replace the simple countdown status window with an edge-docked auto-hide
  floating countdown display.

This feature is not implemented yet.

Expected behavior:

* Show time until the next reminder.
* Stay mostly hidden at the screen edge by default.
* Leave only a small visible tab or handle while hidden.
* Reveal when the mouse pointer touches or hovers over the hidden tab.
* Auto-hide after the pointer leaves or after a short delay.
* Avoid stealing focus while the user works.
* Start with one predictable edge position before adding multi-edge
  customization.

Do not start packaging or startup integration before tray behavior and icon
behavior are stable.
