# EyeBreak

EyeBreak is a small Windows eye-break reminder built with Python, Tkinter, and
`pystray`.

It reminds the user to look far away after a configurable interval, shows a
draggable floating countdown, and provides tray-menu controls for common actions.

## Current Status

Implemented:

* Draggable floating countdown showing time until the next reminder.
* Floating countdown can be moved anywhere on screen.
* Floating countdown remembers its last position after normal app exit.
* Floating countdown auto-hides only when docked to a screen edge.
* Floating countdown stays fully visible when it is not edge-docked.
* Hidden floating countdown skips visible number redraws and refreshes immediately when revealed.
* Floating countdown marks pause state with "暂停中", idle state with "已离开", and fullscreen state with "全屏中".
* Idle detection (5 minutes by default) — when the user is away, reminders pause automatically and resume when they return.
* Fullscreen detection — when a fullscreen app is active, reminders are delayed and resume after fullscreen exits.
* System tray menu powered by `pystray`, including a floating-window toggle and settings window.
* Autostart toggle in the tray menu, persistent through Windows registry (HKCU\...\Run).
* Topmost reminder popup with break countdown.
* Skip, pause, resume, immediate break, and exit flows.
* Mouse-wheel pause-duration adjustment on the reminder popup pause button.
* Custom EyeBreak icon used by the tray, Tkinter reminder window, and Windows taskbar grouping.
* Tray pause menu with selectable pause durations:

  * 5 minutes;
  * 15 minutes;
  * 30 minutes;
  * 60 minutes;
  * 120 minutes.

* JSON configuration for reminder interval, break duration, pause duration, idle threshold, and fullscreen detection.
* Tray settings window for editing reminder interval, break duration, default pause duration, idle threshold, and fullscreen detection without manually editing `config.json`.

Pending manual acceptance:

* None at this point.

Not implemented yet:

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
* Current draggable floating countdown and position-persistence update accepted by the user.
* Idle detection behavior accepted by the user.
* Autostart toggle behavior accepted by the user.
* PyInstaller build output accepted by the user.
* Tray check-mark immediate-refresh behavior accepted by the user.
* Tray settings window behavior accepted by the user.
* Fullscreen detection behavior accepted by the user.

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

Last known automated result: `64 passed` with the command above after escalated rerun.

## Build

Build a standalone Windows executable with PyInstaller:

```powershell
pip install pyinstaller
python -m PyInstaller build.spec
```

The output is `dist/EyeBreak.exe`. Copy the entire `dist/` folder to another
machine; no Python installation is needed.

> **Note:** `config.json` and `app_state.json` are read from the app folder, not
> from the current working directory. In packaged builds, place them alongside
> `EyeBreak.exe`.

Environment note:

* Use `--basetemp=.tmp\pytest` to avoid temp/cache write issues in restricted
  environments.
* In this Windows sandbox, ordinary-permission pytest may fail while cleaning
  `.tmp\pytest` with `PermissionError: [WinError 5]`; the escalated rerun passed.

## Acceptance Checklist

Before a UI milestone is considered accepted, manually verify the relevant flow.

### Floating Countdown

* On startup, only a narrow tab is visible on the right edge of the screen.
* Moving the mouse pointer onto the tab reveals the countdown panel and immediately refreshes the displayed time.
* Dragging the panel away from every screen edge leaves it fully visible and disables auto-hide.
* Dragging the panel to the left, right, top, or bottom edge docks it to that edge.
* When docked, moving the mouse pointer outside the panel hides it immediately and leaves only the tab visible.
* The bright tab stays on the inside edge: left side when docked right, right side when docked left, bottom when docked top, and top when docked bottom.
* The countdown panel shows time until the next reminder.
* The countdown text updates once per second while the panel is visible.
* While the panel is hidden, the app keeps timing reminders but skips visible number redraws until reveal.
* During pause, the panel title says "暂停中" and the remaining pause time is yellow.
* When the user is idle (away from keyboard/mouse) for the `idle_threshold_minutes`, the panel title says "已离开" in gray.
* When a fullscreen app is active, the panel title says "全屏中" in blue and reminders are delayed.
* After exiting and starting again, the floating panel returns to its last saved position.
* After pause ends, reminders resume and the floating panel shows the next reminder countdown.
* The tray menu item "开关悬浮窗" hides and shows the floating countdown without stopping reminders.
* The floating panel stays above normal windows without becoming a full workflow screen.

### Basic Reminder Flow

* Short interval reminder appears when the countdown reaches zero.
* Reminder popup appears centered and topmost.
* Reminder popup countdown decreases once per second.
* Reminder popup closes automatically when countdown reaches zero.
* Skip closes the popup and starts the next reminder interval.
* Exit from the reminder popup terminates the app.

### Idle Detection

* When the user is away from the computer for `idle_threshold_minutes` (default 5), the floating countdown panel changes to "已离开" and reminders stop appearing.
* When the user returns (moves the mouse or presses a key), the reminder interval restarts from the beginning.
* Set `idle_threshold_minutes` to `0` in `config.json` to disable idle detection.


### Fullscreen Detection

* When a fullscreen game, video, or presentation is active, the reminder popup does not appear.
* The floating countdown panel changes to "全屏中" and shows `--:--` while fullscreen is active.
* After exiting fullscreen, the next reminder interval restarts from the beginning.
* The settings window checkbox "全屏时延后提醒" can disable or enable this behavior.
* Non-fullscreen foreground windows do not delay reminders.

### Pause Flow

* Reminder popup pause button uses the default pause duration from `config.json`.
* Mouse wheel over the pause button adjusts the pause duration between 1 and 120
  minutes before clicking pause.
* Pause closes the popup.
* During pause, the floating countdown panel says "暂停中" and shows remaining pause time.
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
* Tray menu item "开关悬浮窗" hides or shows the floating countdown panel.
* Tray menu item "开机自启" toggles the EyeBreak entry in Windows registry
  (HKCU\...\Run). When checked, the app starts automatically on user login.
  Tray menu item "退出" terminates the app and removes the tray icon.


### Settings Window

* Tray menu item "设置" opens one settings window; selecting it again focuses the existing window.
* The window shows current reminder interval, break duration, default pause duration, idle detection threshold, and fullscreen detection toggle.
* Saving valid values writes `config.json`.
* Invalid values show an error and do not overwrite `config.json`.
* Saved reminder interval takes effect immediately for the next reminder countdown.
* If reminders are currently paused, saving settings keeps the current pause deadline and updates the reminder scheduled after the pause ends.
* Setting idle detection to `0` disables idle detection.
* Unchecking "全屏时延后提醒" disables fullscreen-based reminder delay.

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

Fullscreen detection has been implemented and accepted. Next:

* Consider a lightweight release/version note for accepted desktop builds.
