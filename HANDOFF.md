# EyeBreak Handoff

## Maintenance Rule

After every code write or code modification, update this file in the same turn.
The goal is that a new developer who has never seen this project can quickly
understand the current state, what changed, how to run it, and what remains.

## Project Goal

EyeBreak is a small Windows eye-break reminder. The MVP reminds the user at a
fixed interval to look far away for a short countdown, with controls to skip the
current break, pause reminders, resume reminders, trigger a break immediately,
or exit.

The project deliberately avoids non-MVP scope for now: accounts, cloud sync,
daily reports, AI analysis, camera detection, full pomodoro behavior, packaging,
and startup integration are not part of the current baseline.

## Current Baseline

Implemented:

- Small topmost countdown status window showing time until the next reminder.
- Tkinter countdown reminder window.
- Topmost centered reminder popup.
- System tray icon using `pystray`, with menu actions: immediate break, pause,
  resume, and exit.
- Configurable reminder interval, break duration, and pause duration through
  `config.json`.
- Skip current reminder.
- Pause reminders for a duration selected in the reminder window. The default
  comes from `config.json`, and the reminder popup pause button can be adjusted
  with the mouse wheel from 1 to 120 minutes in 5-minute steps.
- During pause, the status window shows remaining pause time; after pause ends,
  the next reminder countdown continues without skipping the reminder.
- Exit from the reminder window, countdown status window, or tray menu.
- Config tests for default creation, custom config loading, and invalid config
  fallback.
- Timer display tests for `MM:SS` formatting.
- Tray icon image generation test.
- Tray pause menu action callback arity fix: `pystray.MenuItem` accepts at
  most two action parameters, so submenu callbacks use a two-argument closure
  factory instead of a lambda with a default parameter.

User-reported acceptance:

- The user reported that the initial MVP acceptance had no issues after testing
  the original reminder flow.
- The user reported that the simple countdown status window acceptance had no
  issues.
- The system tray behavior was accepted by the user.
- The tray pause-duration submenu was accepted by the user; every pause duration was confirmed to take effect.

## File Map

- `main.py`: program entrypoint. Loads config, creates app state, starts timer.
- `config.json`: user-editable runtime configuration.
- `app/config.py`: config dataclass, default config, JSON load/save, fallback
  handling for invalid values.
- `app/state.py`: mutable runtime state shared by timer and UI callbacks,
  including `paused_until` and `next_reminder_at`.
- `app/timer.py`: Tkinter `after()` scheduling loop, topmost countdown status
  window, pause handling, tray callback routing, and reminder window launch.
- `app/reminder_window.py`: Tkinter popup UI, countdown, skip/pause/exit
  callbacks, mouse-wheel pause-duration adjustment, and optional parent window
  support.
- `app/tray.py`: `pystray` tray icon wrapper, generated Pillow icon image,
  and pause-duration submenu options.
- `tests/test_config.py`: config loader tests.
- `tests/test_timer.py`: timer display formatting tests.
- `tests/test_tray.py`: tray icon image generation, pause label, pause option,
  and pause submenu callback tests.
- `requirements.txt`: runtime dependencies for tray support.
- `README.md`: user-facing project overview, install/run/test instructions,
  current acceptance status, and release discipline.
- `MVP软件开发.md`: original product and implementation roadmap.
- `github仓库地址.md`: repository address note.
- `AGENTS.md`: project-level AI agent coding rules, including dependency-first
  implementation guidance and the handoff update requirement.


## README And Release Discipline

At each key development milestone, update `README.md` before asking the user to
accept the work. The README should include current behavior, install/run/test
commands, and the manual acceptance status.

Local commits are allowed at development milestones after `README.md` and
`HANDOFF.md` are updated and relevant tests pass. Do not push before user
acceptance. Only after the user explicitly says acceptance has no issues, for
example "验收没有问题", should the accepted milestone be pushed to GitHub.

This rule is also recorded in `AGENTS.md` so future AI coding agents follow it.

## Agent Coding Rules

`AGENTS.md` defines project-level rules for future AI coding agents. The most
important rule is dependency-first implementation: before hand-writing a feature,
check whether a mature package, plugin, or standard-library module can directly
provide it. Use the existing implementation when it solves the requirement
without broadening scope or forcing a rewrite.

This is especially relevant for tray icons, Windows startup integration, global
hotkeys, idle detection, fullscreen detection, packaging, installers, and
background scheduling.

Dependency decisions:

- Countdown status window: no external package was added. Tkinter's standard
  `after()` scheduling and labels directly satisfy the simple acceptance-oriented
  countdown display.
- System tray: `pystray==0.19.5` was added because tray icons and menus are
  platform integration that should not be hand-written against Windows APIs for
  this MVP. Pillow is also listed because `pystray` uses Pillow images and the
  app generates its tray icon at runtime.

## Run

Install dependencies if needed:

```powershell
python -m pip install -r requirements.txt
```

Run the app:

```powershell
python main.py
```

For faster manual testing, temporarily edit `config.json`, for example:

```json
{
  "reminder_interval_minutes": 0.1667,
  "break_duration_seconds": 10,
  "pause_minutes": 1
}
```

Restore production-like values after testing:

```json
{
  "reminder_interval_minutes": 25,
  "break_duration_seconds": 20,
  "pause_minutes": 60
}
```

## Test

Use:

```powershell
python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest
```

Last known automated result:

- `9 passed` after fixing tray pause submenu callback arity and adding callback coverage.

Known environment note:

- The sandbox previously blocked pytest temp/cache writes unless `--basetemp`
  was set, and escalation was needed once to run the test command successfully.

## Manual Acceptance Checklist

Before calling a UI change done, verify:

- Countdown status window appears on startup.
- Countdown status window updates once per second.
- Tray icon appears in the Windows system tray.
- Tray menu item "立即休息" opens the reminder popup immediately.
- Tray menu item "暂停" opens selectable durations: 5, 15, 30, 60, and
  120 minutes.
- Selecting a tray pause duration pauses for that chosen duration, not the fixed
  configured default.
- Tray menu item "恢复" clears pause and starts a fresh reminder countdown.
- Tray menu item "退出" terminates the app and removes the tray icon.
- Short interval reminder appears when the countdown reaches zero.
- Reminder popup countdown decreases once per second.
- Reminder popup closes automatically when countdown reaches zero.
- Skip closes the popup and starts the next reminder interval.
- Mouse wheel over the pause button adjusts the pause duration between 1 and
  120 minutes before clicking pause.
- Pause closes the popup and the status window shows remaining pause time.
- After pause ends, the next reminder countdown restarts.
- Exit from the reminder popup or status window terminates the process.

## Next Development Options

Recommended next step:

- Tray pause-duration submenu has been manually accepted; next work should start from a new unaccepted milestone.
- Planned user-requested feature: replace the simple countdown status window with
  an edge-docked auto-hide floating countdown display. It should stay mostly
  hidden at the screen edge and reveal itself when the mouse pointer touches or
  hovers over the hidden tab.

Do not start with packaging or startup integration before the tray behavior is
stable.

Floating countdown design notes:

- It should show time until the next reminder, not the 20-second break countdown
  only.
- Default state should be edge-docked and mostly hidden, with only a small tab or
  handle visible.
- It should reveal on mouse hover/touch near the hidden tab, then auto-hide again
  after the pointer leaves or after a short delay.
- It should not steal focus while the user works.
- It should support at least one predictable edge position before adding
  multi-edge customization.
- Implementing it cleanly likely requires exposing timer state, which is now
  partly available through `AppState.next_reminder_at` and `paused_until`.
