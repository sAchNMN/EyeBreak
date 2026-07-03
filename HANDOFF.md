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

* Automated tests: `18 passed` with
  `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest`.
* Manual acceptance passed:

  * original reminder flow;
  * earlier simple countdown status window before it was replaced;
  * system tray behavior;
  * tray pause-duration submenu;
  * generated app/tray/window/taskbar icon visual check on Windows.
* Pending manual acceptance:

  * right-edge docked auto-hide floating countdown display.
* Push rule:

  * do not push before explicit user acceptance, such as "验收没有问题".

## Current Change Pending Acceptance

Floating countdown development started after the accepted icon milestone.

Changed files:

* `app/floating_countdown.py` added.
* `app/timer.py` updated to use `FloatingCountdownWindow` for the countdown display.
* `tests/test_floating_countdown.py` added.
* `tests/test_timer.py` updated with a floating countdown wiring guard.
* `README.md` updated for user-visible floating countdown behavior and acceptance checklist.
* `HANDOFF.md` updated for this handoff.

Current behavior:

* The old fixed countdown status window has been replaced by a borderless,
  right-edge docked floating panel.
* On startup, the panel hides off the right edge and leaves a `10px` visible tab.
* Mouse enter on the visible tab reveals the full `188x64` panel.
* Mouse leave schedules a `700ms` delayed hide.
* Before hiding, the panel checks whether the pointer is still inside the window;
  this avoids hiding during parent/child widget transitions.
* The existing timer state still drives the text:

  * normal countdown uses white text;
  * pause countdown uses yellow text;
  * reminder triggering, pause, resume, skip, tray controls, and exit behavior are unchanged.

Dependency decision:

* No new package was added.
* Tkinter geometry, event bindings, and `after()` are enough for this first
  acceptance-oriented floating display.

Test history for this change:

* Ordinary run after the timer guard: `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest`
  returned `14 passed, 4 errors`; the errors were the known Windows sandbox
  `.tmp\pytest` cleanup `PermissionError: [WinError 5]`, not assertion failures.
* Escalated rerun of the same command passed after the pointer-inside hide guard:
  `18 passed in 0.22s`.

Known limitation:

* The floating countdown has automated coverage for geometry helpers and timer
  wiring, but reveal/hide feel still requires manual Windows UI acceptance.

## Current Baseline

Implemented:

* Right-edge docked auto-hide floating countdown showing time until the next reminder.
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
* During pause, the floating countdown panel shows remaining pause time.
* After pause ends, reminders resume and the floating countdown panel shows the
  next reminder countdown.
* Exit from the reminder window, floating countdown panel, or tray menu.
* Config tests for default creation, custom config loading, and invalid config
  fallback.
* Timer display and floating countdown wiring tests.
* Custom generated EyeBreak icon stored at `assets/eyebreak.ico`.
* Tray icon, Tkinter window icons, and Windows taskbar grouping share the
  generated EyeBreak icon path.
* Tray pause menu action callback arity fix:

  * `pystray.MenuItem` accepts at most two action parameters;
  * submenu callbacks use a two-argument closure factory instead of a lambda with
    a default parameter.

## User-Reported Acceptance

Accepted by the user:

* Initial MVP reminder flow had no issues after manual testing.
* Earlier simple countdown status window had no issues.
* System tray behavior had no issues.
* Tray pause-duration submenu had no issues.
* Every tray pause duration was confirmed to take effect.
* Generated app/tray/window/taskbar icon behavior was confirmed to have no
  issues by the user.

Not accepted yet:

* Right-edge docked auto-hide floating countdown display.

## File Map

* `main.py`: program entrypoint. Loads config, creates app state, starts timer.
* `config.json`: user-editable runtime configuration.
* `app/config.py`: config dataclass, default config, JSON load/save, fallback
  handling for invalid values.
* `app/state.py`: mutable runtime state shared by timer and UI callbacks,
  including `paused_until` and `next_reminder_at`.
* `app/timer.py`: Tkinter `after()` scheduling loop, floating countdown
  integration, pause handling, tray callback routing, Windows taskbar AppUserModelID
  setup before root-window creation, and reminder window launch.
* `app/floating_countdown.py`: right-edge docked auto-hide floating countdown
  window, geometry helpers, reveal-on-enter, delayed hide-on-leave behavior, and
  pointer-inside guard before hiding.
* `app/reminder_window.py`: Tkinter popup UI, countdown, skip/pause/exit
  callbacks, mouse-wheel pause-duration adjustment, and optional parent window
  support.
* `app/tray.py`: `pystray` tray icon wrapper, generated Pillow icon image, and
  pause-duration submenu options.
* `tests/test_config.py`: config loader tests.
* `tests/test_floating_countdown.py`: floating countdown geometry helper tests.
* `tests/test_icons.py`: generated icon image, `.ico` file creation, and Windows
  AppUserModelID smoke tests.
* `tests/test_timer.py`: timer display formatting and floating countdown wiring
  tests.
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

* Escalated run passed: `18 passed in 0.22s`.
* Ordinary-permission run can fail during `.tmp\pytest` cleanup with
  `PermissionError: [WinError 5]` in this Windows sandbox.

## Manual Acceptance Checklist

Before calling the floating countdown done, verify:

* On startup, only a narrow tab is visible on the right edge of the screen.
* Moving the mouse pointer onto the tab reveals the countdown panel.
* Moving the mouse pointer away hides the panel again after a short delay.
* The countdown panel shows time until the next reminder.
* The countdown text updates once per second.
* During pause, the countdown panel shows remaining pause time in yellow.
* After pause ends, reminders resume and the floating panel shows the next reminder countdown.
* Tray pause/resume/immediate-break/exit flows still work.
* Reminder popup still opens when the countdown reaches zero.

## Known Pending Work

Pending manual validation:

* Right-edge auto-hide floating countdown display.

Possible next refinement after acceptance:

* Tune the hidden tab width or reveal delay if the manual feel is too sensitive or too hard to trigger.

Do not start packaging or startup integration before tray behavior, icon
behavior, and floating countdown behavior are stable.