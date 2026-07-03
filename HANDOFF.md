# EyeBreak Handoff

## Maintenance Rule

After every task that makes a meaningful code, behavior, dependency, command, or
test change, update this file before reporting the task complete.

The goal is that a new developer who has never seen this project can quickly
understand the current state, what changed, how to run it, how to test it, and
what remains.

## Project Goal

EyeBreak is a small Windows eye-break reminder.

The MVP reminds the user at a fixed interval to look far away for a short
countdown, with controls to skip the current break, pause reminders, resume
reminders, trigger a break immediately, or exit.

The project deliberately avoids non-MVP scope for now:

* accounts;
* cloud sync;
* daily reports;
* AI analysis;
* camera detection;
* full pomodoro behavior;
* packaging;
* startup integration.

## Current Status

* Automated tests: `11 passed` with
  `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest`.
* Manual acceptance passed:

  * original reminder flow;
  * simple countdown status window;
  * system tray behavior;
  * tray pause-duration submenu.
* Manual acceptance pending:

  * generated app/tray/window icon visual check on Windows.
* Not implemented yet:

  * edge-docked auto-hide floating countdown display.
* Push rule:

  * do not push before explicit user acceptance, such as "验收没有问题".

## Current Baseline

Implemented:

* Small topmost countdown status window showing time until the next reminder.
* Tkinter countdown reminder window.
* Topmost centered reminder popup.
* System tray icon using `pystray`.
* Tray menu actions:

  * immediate break;
  * pause;
  * resume;
  * exit.
* Configurable reminder interval, break duration, and pause duration through
  `config.json`.
* Skip current reminder.
* Pause reminders for a selected duration in the reminder window.
* Reminder popup pause duration defaults to `config.json`.
* Reminder popup pause button can be adjusted with the mouse wheel from 1 to 120
  minutes in 5-minute steps.
* During pause, the status window shows remaining pause time.
* After pause ends, reminders resume and the status window shows the next
  reminder countdown.
* Exit from the reminder window, countdown status window, or tray menu.
* Config tests for default creation, custom config loading, and invalid config
  fallback.
* Timer display tests for `MM:SS` formatting.
* Custom generated EyeBreak icon stored at `assets/eyebreak.ico`.
* Tray icon and Tkinter window icons share the same generated icon source.
* Tray icon image generation test.
* Tray pause menu action callback arity fix:

  * `pystray.MenuItem` accepts at most two action parameters;
  * submenu callbacks use a two-argument closure factory instead of a lambda with
    a default parameter.

## User-Reported Acceptance

Accepted by the user:

* Initial MVP reminder flow had no issues after manual testing.
* Simple countdown status window had no issues.
* System tray behavior had no issues.
* Tray pause-duration submenu had no issues.
* Every tray pause duration was confirmed to take effect.

Pending acceptance:

* Icon implementation is automated-test covered, but visual UI acceptance on
  Windows is still pending.

## File Map

* `main.py`: program entrypoint. Loads config, creates app state, starts timer.
* `config.json`: user-editable runtime configuration.
* `app/config.py`: config dataclass, default config, JSON load/save, fallback
  handling for invalid values.
* `app/state.py`: mutable runtime state shared by timer and UI callbacks,
  including `paused_until` and `next_reminder_at`.
* `app/timer.py`: Tkinter `after()` scheduling loop, topmost countdown status
  window, pause handling, tray callback routing, and reminder window launch.
* `app/reminder_window.py`: Tkinter popup UI, countdown, skip/pause/exit
  callbacks, mouse-wheel pause-duration adjustment, and optional parent window
  support.
* `app/tray.py`: `pystray` tray icon wrapper, generated Pillow icon image, and
  pause-duration submenu options.
* `tests/test_config.py`: config loader tests.
* `tests/test_icons.py`: generated icon image and `.ico` file creation tests.
* `tests/test_timer.py`: timer display formatting tests.
* `tests/test_tray.py`: tray icon image generation, pause label, pause option,
  and pause submenu callback tests.
* `requirements.txt`: runtime dependencies for tray support.
* `README.md`: user-facing project overview, install/run/test instructions,
  current acceptance status, and release discipline.
* `MVP软件开发.md`: original product and implementation roadmap.
* `github仓库地址.md`: repository address note.
* `AGENTS.md`: project-level AI agent coding rules.
* `.gitignore`: excludes Python cache/test temp files and local tool artifacts such
  as `.mimocode/` and `mimo.exe`.

## README And Release Discipline

Follow `AGENTS.md` as the source of truth for README, commit, test, and push
rules.

Current release rule summary:

* Update `README.md` before milestone acceptance when user-visible behavior,
  install commands, run commands, test commands, dependencies, or acceptance
  status changes.
* Commit only after relevant tests pass and `HANDOFF.md` / `README.md` are
  updated when required.
* Inspect `git status` before committing.
* Exclude unrelated, temporary, local IDE, cache, or scratch files from commits.
* `mimo.exe` is larger than GitHub ordinary file limits and must stay local unless
  Git LFS or another release-asset flow is intentionally introduced.
* Do not claim tests passed unless they were actually run in the current
  environment.
* Report exact test commands and results when reporting completion.
* Do not push before explicit user acceptance, such as "验收没有问题".
* Push only the accepted milestone to GitHub.

## Agent Coding Rules Summary

`AGENTS.md` is the source of truth for future AI coding agents.

Important summary:

* Keep scope surgical.
* Default to no new dependency.
* Consider existing standard-library, Tkinter, project-code, or mature package
  solutions before hand-writing fragile platform integration.
* Add or prefer an external dependency only when it clearly reduces
  implementation risk, complexity, or platform-specific behavior without
  expanding scope.
* Record dependency decisions in `HANDOFF.md`.
* Report exact test commands and results.
* Do not push before explicit user acceptance.
* Do not modify `AGENTS.md` unless the user explicitly asks for project
  instruction changes.

## Dependency Decisions

* Countdown status window:

  * no external package was added;
  * Tkinter's standard `after()` scheduling and labels directly satisfy the
    simple acceptance-oriented countdown display.

* System tray:

  * `pystray==0.19.5` was added;
  * tray icons and menus are platform integration that should not be hand-written
    against Windows APIs for this MVP;
  * Pillow is also listed because `pystray` uses Pillow images and the app
    generates its tray icon at runtime.

## Run

Install dependencies if needed:

```powershell
python -m pip install -r requirements.txt
```

Run the app:

```powershell
python main.py
```

For faster manual testing, temporarily edit `config.json`:

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

* `11 passed` after generated application icon tests and the tray pause submenu
  callback arity fix.

Known environment note:

* Use `--basetemp=.tmp\pytest` to avoid temp/cache write issues in restricted
  environments.

## Manual Acceptance Checklist

Before calling a UI change done, verify:

* Countdown status window appears on startup.
* Countdown status window updates once per second.
* Tray icon appears in the Windows system tray.
* Countdown status window shows the EyeBreak title-bar icon.
* Reminder popup shows the EyeBreak title-bar icon.
* Tray menu item "立即休息" opens the reminder popup immediately.
* Tray menu item "暂停" opens selectable durations:

  * 5 minutes;
  * 15 minutes;
  * 30 minutes;
  * 60 minutes;
  * 120 minutes.
* Selecting a tray pause duration pauses for that chosen duration, not the fixed
  configured default.
* Tray menu item "恢复" clears pause and starts a fresh reminder countdown.
* Tray menu item "退出" terminates the app and removes the tray icon.
* Short interval reminder appears when the countdown reaches zero.
* Reminder popup countdown decreases once per second.
* Reminder popup closes automatically when countdown reaches zero.
* Skip closes the popup and starts the next reminder interval.
* Mouse wheel over the pause button adjusts the pause duration between 1 and 120
  minutes before clicking pause.
* Pause closes the popup and the status window shows remaining pause time.
* After pause ends, reminders resume and the status window shows the next
  reminder countdown.
* Exit from the reminder popup or status window terminates the process.

## Known Pending Work

Pending manual validation:

* Manually validate the generated tray icon and window title-bar icon on Windows.

Planned user-requested feature:

* Replace the simple countdown status window with an edge-docked auto-hide
  floating countdown display.

This floating countdown feature is not implemented yet.

Do not start packaging or startup integration before tray behavior and icon
behavior are stable.

## Floating Countdown Design Notes

The planned floating countdown should:

* show time until the next reminder, not only the 20-second break countdown;
* stay edge-docked and mostly hidden by default;
* leave only a small tab or handle visible while hidden;
* reveal itself when the mouse pointer touches or hovers over the hidden tab;
* auto-hide again after the pointer leaves or after a short delay;
* avoid stealing focus while the user works;
* support at least one predictable edge position before adding multi-edge
  customization.

Implementation note:

* Implementing this cleanly likely requires exposing timer state.
* Timer state is now partly available through `AppState.next_reminder_at` and
  `AppState.paused_until`.
