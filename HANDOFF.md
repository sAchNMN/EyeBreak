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
reminders, trigger a break immediately, toggle the floating countdown, or exit.

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

## Current Autostart Runtime Path Fix

User reported PyInstaller startup crashes on Windows login:

* `PermissionError: [Errno 13] Permission denied: 'config.json'`
* traceback entered through `main.py -> load_config() -> save_config()`
* after the config fix, startup still failed with `PermissionError: [WinError 5]` on `assets`
* second traceback entered through `main.py -> ReminderTimer.run() -> ensure_icon_file()`

Root cause:

* `CONFIG_PATH = Path("config.json")` depended on the process current working directory.
* `ICON_PATH = Path("assets") / "eyebreak.ico"` had the same cwd dependency.
* Windows Run-key autostart does not guarantee the app folder as cwd, so startup could try to create runtime files in a protected directory.

Changed files:

* `app/paths.py` (new)
* `app/config.py`
* `app/icons.py`
* `app/state.py`
* `tests/test_paths.py` (new)
* `tests/test_config.py`
* `tests/test_icons.py`
* `tests/test_state.py`
* `README.md`
* `HANDOFF.md`

Current behavior:

* Source runs resolve runtime files from the project root.
* Frozen PyInstaller runs resolve runtime files from the `EyeBreak.exe` folder.
* `config.json`, `app_state.json`, and `assets/eyebreak.ico` no longer depend on Windows autostart cwd.
* Missing `config.json` still returns defaults if the default file cannot be created.
* `assets/eyebreak.ico` creation failure is ignored; Tkinter/Pillow fallback icon creation can still run without that file.
* `app_state.json` write failure during exit is ignored because floating-window position persistence is optional.

Dependency decision:

* No new dependency was added.
* Python standard-library `sys` and `pathlib` are enough for path resolution.

Test commands and results:

* Ordinary config-path targeted run: `python -m pytest -q tests\test_config.py tests\test_state.py tests\test_paths.py tests\test_autostart.py -p no:cacheprovider --basetemp=.tmp\pytest` returned `14 passed, 9 errors`; errors were the known Windows sandbox `.tmp\pytest` cleanup `PermissionError`, not assertion failures.
* Escalated config-path targeted rerun passed: `25 passed in 0.15s`.
* Ordinary icon-path targeted run: `python -m pytest -q tests\test_icons.py tests\test_paths.py tests\test_config.py tests\test_state.py tests\test_autostart.py -p no:cacheprovider --basetemp=.tmp\pytest` returned `20 passed, 11 errors`; errors were the same sandbox `.tmp\pytest` cleanup `PermissionError`, not assertion failures.
* Escalated icon-path targeted rerun passed: `31 passed in 0.33s`.
* Escalated full regression after config fix passed: `71 passed in 0.46s` with `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest`.
* Escalated full regression after icon fix passed: `73 passed in 0.35s` with the same full-test command.
* First PyInstaller rebuild attempt failed on `build\build\base_library.zip` with `PermissionError: [WinError 5]`.
* Escalated rebuild then failed because two old `EyeBreak.exe` processes were still holding `dist\EyeBreak.exe`.
* Stopped old EyeBreak processes `13500` and `13876`.
* Final escalated rebuild passed with `python -m PyInstaller build.spec`; output is `dist\EyeBreak.exe`.
* Smoke run passed: started `dist\EyeBreak.exe`, waited 3 seconds, confirmed process `5012` was still running, then stopped it.

Manual acceptance status:

* Rebuilt executable smoke test passed.
* User confirmed acceptance in this turn.

* Git status at takeover: clean and synced with `origin/master`.
* Automated tests: `44 passed` with
  `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` after escalated rerun.
* Ordinary-permission test run returned `36 passed, 8 errors`; errors were the known Windows sandbox `.tmp\pytest` cleanup `PermissionError: [WinError 5]`, not assertion failures.
* Manual acceptance passed:

  * original reminder flow;
  * earlier simple countdown status window before it was replaced;
  * system tray behavior;
  * tray pause-duration submenu;
  * generated app/tray/window/taskbar icon visual check on Windows;
  * draggable floating countdown and position persistence milestone;
  * idle detection behavior.
* Pending manual acceptance:

  * none at this point.
* Push rule:

  * do not push before explicit user acceptance, such as "验收没有问题".

## Current Change Pending Acceptance

This side-conversation request added a more complete floating countdown behavior.

Changed files:

* `app/floating_countdown.py`
* `app/state.py`
* `app/timer.py`
* `app/tray.py`
* `tests/test_floating_countdown.py`
* `tests/test_timer.py`
* `tests/test_tray.py`
* `README.md`
* `HANDOFF.md`

Current behavior:

* The floating countdown can be dragged to any screen position.
* If the window is not near a screen edge when released, it remains fully visible
  and does not auto-hide.
* If the window is released within `12px` of the left, right, top, or bottom edge,
  it snaps to that edge and becomes edge-docked.
* When edge-docked, mouse leave hides the panel immediately and leaves only a
  `10px` tab visible.
* Moving the mouse onto the visible tab reveals the full `188x64` panel.
* During pause, the title changes to `暂停中` and the remaining pause time is yellow.
* The tray menu has a `开关悬浮窗` item. It hides or shows the floating countdown
  without stopping reminders.
* Reminder triggering, pause, resume, skip, tray pause choices, and exit behavior
  remain driven by the existing timer state.

Dependency decision:

* No new package was added.
* Tkinter mouse events, geometry, `withdraw()` / `deiconify()`, and existing
  `pystray` menu support are enough for this feature.

Test history for this change:

* Ordinary run: `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest`
  returned `20 passed, 4 errors`; the errors were the known Windows sandbox
  `.tmp\pytest` cleanup `PermissionError: [WinError 5]`, not assertion failures.
* Escalated rerun of the same command passed before the tab-orientation fix: `24 passed in 0.30s`.
* Tab-orientation fix rerun passed: `25 passed in 0.23s`.

Known limitation:

* Automated tests cover geometry helpers, tray callback wiring, and timer toggle
  state. Real drag feel, edge snapping feel, immediate hide behavior, and tray UI
  behavior still need manual Windows acceptance.

## Current Baseline

Implemented:

* Draggable floating countdown showing time until the next reminder.
* Edge-docked auto-hide only when the floating countdown is docked to a screen edge.
* Non-docked floating countdown stays fully visible.
* Pause status label in the floating countdown.
* Tray menu item to toggle the floating countdown.
* Tkinter countdown reminder window.
* Topmost centered reminder popup.
* System tray icon using `pystray`.
* Tray menu actions:

  * immediate break;
  * pause duration submenu;
  * resume;
  * toggle floating countdown;
  * exit.
* Configurable reminder interval, break duration, and pause duration through
  `config.json`.
* Skip current reminder.
* Pause reminders for a selected duration in the reminder window.
* Reminder popup pause duration defaults to `config.json`.
* Reminder popup pause button can be adjusted with the mouse wheel from 1 to 120
  minutes in 5-minute steps.
* During pause, the floating countdown panel shows remaining pause time and says
  `暂停中`.
* After pause ends, reminders resume and the floating countdown panel shows the
  next reminder countdown.
* Exit from the reminder window, floating countdown panel, or tray menu.
* Config tests for default creation, custom config loading, and invalid config
  fallback.
* Timer display and floating countdown wiring tests.
* Floating countdown geometry tests for docking and hidden positions.
* Tray tests for pause menu and floating toggle callback.
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

* None at this point.

Accepted later:

* Draggable floating countdown update and position persistence.
* Idle detection feature — user confirmed acceptance with 验收没有问题.
* Autostart toggle behavior — user confirmed it has been accepted.
* PyInstaller build output — user confirmed it has been accepted.
* Tray check-mark immediate-refresh behavior — user confirmed it has been accepted.

## File Map

* `main.py`: program entrypoint. Loads config, creates app state, starts timer.
* `config.json`: user-editable runtime configuration.
* `app/config.py`: config dataclass, default config, JSON load/save, fallback
  handling for invalid values.
* `app/state.py`: mutable runtime state shared by timer and UI callbacks,
  including `paused_until`, `next_reminder_at`, and `floating_countdown_enabled`.
* `app/timer.py`: Tkinter `after()` scheduling loop, floating countdown
  integration, pause status updates, tray callback routing, Windows taskbar
  AppUserModelID setup before root-window creation, and reminder window launch.
* `app/floating_countdown.py`: draggable floating countdown window, edge docking,
  hidden-tab positions, reveal-on-enter, immediate docked hide-on-leave, pause
  status text, and enable/disable behavior.
* `app/reminder_window.py`: Tkinter popup UI, countdown, skip/pause/exit
  callbacks, mouse-wheel pause-duration adjustment, and optional parent window
  support.
* `app/tray.py`: `pystray` tray icon wrapper, generated Pillow icon image, pause
  duration submenu, and floating countdown toggle action.
* `tests/test_config.py`: config loader tests.
* `tests/test_floating_countdown.py`: floating countdown geometry helper tests.
* `tests/test_icons.py`: generated icon image, `.ico` file creation, and Windows
  AppUserModelID smoke tests.
* `tests/test_timer.py`: timer display formatting and floating countdown toggle
  tests.
* `tests/test_tray.py`: tray icon image generation, pause label, pause submenu,
  and floating toggle callback tests.
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

* Escalated takeover run passed: `44 passed in 0.30s`.
* Ordinary-permission run can fail during `.tmp\\pytest` cleanup with
  `PermissionError: [WinError 5]` in this Windows sandbox.

## Manual Acceptance Checklist

Before calling the draggable floating countdown done, verify:

* On startup, only a narrow tab is visible on the right edge of the screen.
* Moving the mouse pointer onto the tab reveals the countdown panel.
* Dragging the panel away from every screen edge leaves it fully visible and disables auto-hide.
* Dragging the panel to the left, right, top, or bottom edge docks it to that edge.
* When docked, moving the mouse pointer outside the panel hides it immediately and leaves only the tab visible.
* The bright tab stays on the inside edge: left side when docked right, right side when docked left, bottom when docked top, and top when docked bottom.
* The countdown panel shows time until the next reminder and updates once per second.
* During pause, the panel title says `暂停中` and the remaining pause time is yellow.
* After pause ends, reminders resume and the floating panel shows the next reminder countdown.
* Tray menu item `开关悬浮窗` hides and shows the floating countdown without stopping reminders.
* Tray pause/resume/immediate-break/exit flows still work.
* Reminder popup still opens when the countdown reaches zero.

## Known Pending Work

Pending manual validation:

* None at this point.

Possible next refinement after acceptance:

* Tune the docking threshold, hidden tab width, or drag feel if manual acceptance
  shows the interaction is too sensitive or too hard to trigger.

Do not start packaging or startup integration before tray behavior, icon
behavior, and floating countdown behavior are stable.
## Current Tab-Orientation Fix

User clarified the hidden tab orientation requirement:

* right-edge docking: bright tab stays on the left side of the panel;
* left-edge docking: bright tab stays on the right side of the panel;
* top-edge docking: bright tab stays on the bottom side of the panel;
* bottom-edge docking: bright tab stays on the top side of the panel.

Code write:

* Updated `app/floating_countdown.py` so the bright tab frame is dynamically
  repacked according to the current dock edge.
* Rewrote `app/floating_countdown.py` to apply the tab orientation rule and added `tests/test_floating_countdown.py` coverage for right/left/top/bottom tab pack direction.
* Tests have not been rerun after this tab-orientation write and test update.
## Current Top-Edge Tab Visibility Fix

User reported from screenshots that when the floating countdown is docked to the
screen top edge, the bright tab is not visibly shown at the bottom edge of the
floating window.

Code write:

* Updated `app/floating_countdown.py` so `_place_tab_for_edge()` uses deterministic
  `place()` coordinates instead of `pack()` ordering.
* This guarantees the visible 10px strip is the bright tab for all four dock
  edges, especially the top edge where the visible strip is the bottom of the
  mostly-hidden window.
* Updated `tests/test_floating_countdown.py` to assert exact `place()` coordinates for the bright tab on each dock edge.
* Ordinary run after this fix returned `21 passed, 4 errors`; errors were the known Windows sandbox `.tmp\pytest` cleanup `PermissionError`, not assertion failures.
* Escalated rerun passed: `25 passed in 0.24s`.
## Current Hidden Countdown Update Optimization

User requested that when the floating countdown is hidden, the app should stop
updating the visible countdown number to save computer performance. The timer
must still run so reminders remain accurate.

Changed files:

* `app/floating_countdown.py`
* `app/timer.py`
* `tests/test_timer.py`
* `README.md`
* `HANDOFF.md`

Current behavior:

* `FloatingCountdownWindow` tracks `_is_hidden` and exposes
  `should_update_display()`.
* Edge-hide and tray-disable mark the floating panel hidden.
* Reveal and drag mark the floating panel visible.
* `FloatingCountdownWindow.build()` accepts an optional `on_show` callback.
* `ReminderTimer` passes `_update_countdown_display` as `on_show`, so the displayed
  time refreshes immediately when the user reveals the panel.
* `ReminderTimer` still ticks every second for accurate reminder scheduling, but
  hidden panels skip Tk label `configure()` calls for the countdown number and
  pause title.

Test history for this change:

* Ordinary run: `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest`
  returned `23 passed, 4 errors`; the errors were the known Windows sandbox
  `.tmp\pytest` cleanup `PermissionError: [WinError 5]`, not assertion failures.
* Escalated rerun of the same command passed: `27 passed in 0.24s`.

Known limitation:

* This optimization reduces hidden-panel UI redraws, not the timer loop itself.
  The timer loop must keep running so reminders stay accurate.
## Current Floating Position Persistence Work

User requested that the floating countdown remember its position after normal app exit.

Code write completed:

* Updated `app/state.py` with `app_state.json` load/save helpers.
* Persisted state is intentionally limited to the floating countdown edge and visible position.
* Runtime timer values such as pause deadline and next reminder deadline are not persisted.

Dependency decision:

* No new package was added.
* Persistence uses Python standard-library `json` and `pathlib`.

Tests have not been run after this write yet.

Floating countdown write completed:

* Updated `app/floating_countdown.py` so the constructor accepts initial edge, x, and y values.
* Added `placement()` to return the saved visible position instead of hidden-tab geometry.
* Added startup placement logic that clamps old coordinates to the current screen size.
* Edge-docked windows start hidden at the saved dock edge; non-docked windows start fully visible at the saved position.

Tests have not been run after this write yet.

Startup and exit persistence write completed:

* Updated `main.py` to create the runtime state with `load_app_state()`.
* Updated `app/timer.py` to pass saved floating countdown placement into `FloatingCountdownWindow`.
* Updated `app/timer.py` to call `save_app_state()` during normal exit after copying `placement()` from the floating window.

Tests have not been run after this write yet.

Test write completed:

* Added `tests/test_state.py` for `app_state.json` load/save behavior.
* Updated `tests/test_floating_countdown.py` to assert that `placement()` returns visible geometry, not hidden-tab geometry.

Tests have not been run after this write yet.

Documentation and local-state ignore write completed:

* Updated `README.md` to document that the floating countdown restores its last saved position after normal exit.
* Updated `.gitignore` to exclude runtime-created `app_state.json`.

Tests have not been run after this write yet.

Formatting correction completed:

* Fixed literal PowerShell newline-escape text accidentally written into `README.md` and `tests/test_floating_countdown.py`.
* No behavior change beyond restoring valid markdown and Python syntax.

Tests have not been run after this correction yet.

Current floating position persistence verification:

Changed files for this persistence step:

* `.gitignore`
* `app/floating_countdown.py`
* `app/state.py`
* `app/timer.py`
* `main.py`
* `tests/test_floating_countdown.py`
* `tests/test_state.py`
* `README.md`
* `HANDOFF.md`

Current behavior:

* On normal exit, `ReminderTimer._exit()` copies `FloatingCountdownWindow.placement()` into `AppState` and writes `app_state.json`.
* On startup, `main.py` loads `app_state.json` with `load_app_state()` and passes the saved edge/x/y into the floating countdown window.
* Edge-docked placement restores to the same edge and visible coordinate, then starts hidden with only the tab visible.
* Non-docked placement restores as a fully visible floating panel at the saved coordinate.
* Saved coordinates are clamped to the current screen size on startup.
* `app_state.json` is ignored by git because it is local runtime UI state.

Dependency decision:

* No new package was added.
* Python standard-library `json` and `pathlib` are enough for this state file.

Test commands and results:

* Ordinary run: `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest`
  returned `24 passed, 7 errors`; the errors were the known Windows sandbox
  `.tmp\pytest` cleanup `PermissionError: [WinError 5]`, not assertion failures.
* Escalated rerun of the same command passed: `31 passed in 0.34s`.

Manual acceptance status:

* Position persistence has been accepted by the user as part of the floating countdown milestone.

Encoding correction completed:

* Restored UTF-8 BOM on `README.md` and `.gitignore` to avoid unrelated encoding churn in the diff.
* No behavior or content change.

Tests were already run after code changes; no rerun was needed for this encoding-only correction.

## Current Floating Countdown Milestone Accepted

User acceptance:

* User confirmed acceptance with: `验收没问题`.
* The accepted milestone includes draggable floating countdown behavior, edge-docked auto-hide behavior, pause status label, tray floating-window toggle, hidden-display update optimization, and floating-window position persistence.

Commit readiness:

* `README.md` now marks the current milestone as accepted.
* `HANDOFF.md` records this acceptance before commit.
* `CLAUDE.md` remains untracked local state and must not be staged.

## Current Autostart Feature

Changed files:

* `app/autostart.py` (new)
* `app/tray.py`
* `app/timer.py`
* `tests/test_autostart.py` (new)
* `README.md`
* `HANDOFF.md`
* `.gitignore`

Current behavior:

* The tray menu now has a "开机自启" item with a check mark showing the current state.
* Clicking the item toggles the EyeBreak entry in `HKCU\...\Run`.
* When running from Python source, the registered command uses `pythonw.exe main.py` (no console window).
* When running from a PyInstaller-built executable, the registered command uses the exe path directly.
* On user login, EyeBreak starts automatically when the entry is enabled.

Dependency decision:

* No new package was added.
* Python standard-library `winreg` handles the Windows Registry; no external dependency needed.

Test commands and results:

* `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` returned `40 passed in 0.29s`.
* 9 new tests in `tests/test_autostart.py` cover registry write/delete/read and path generation (pythonw/python.exe/frozen).

Manual acceptance status:

* Autostart toggle behavior has been accepted by the user.

## Current PyInstaller Packaging

Changed files:

* uild.spec (new)
* .gitignore
* HANDOFF.md

Current behavior:

* `build.spec` defines a PyInstaller build targeting a single Windows executable with:
  * No console window (console=False);
  * EyeBreak icon from `assets/eyebreak.ico` embedded in the exe;
  * pystray, PIL, winreg as hidden imports;
  * `assets/eyebreak.ico` copied alongside the exe for runtime icon generation.
* Run pyinstaller build.spec to produce dist/EyeBreak/EyeBreak.exe.
* Build artifacts (`dist/`, `build/`) are git-ignored; `build.spec` is tracked.

Dependency decision:

* pyinstaller added as a build-time dependency (not runtime).
* No new runtime package was added.

Manual acceptance status:

* PyInstaller build output has been accepted by the user.

## Current Tray Menu Check Mark Fix

User reported that tray menu items "开关悬浮窗" and "开机自启" showed no on/off state.

Changed files:

* `app/tray.py`
* `app/timer.py`
* `HANDOFF.md`

Current behavior:

* "开关悬浮窗" now has `checked=lambda item: get_is_floating_enabled()` which reads `state.floating_countdown_enabled`.
* "开机自启" now has `checked=lambda item: get_is_autostart_enabled()` which calls `is_autostart_enabled()`.
* Both items show a check mark when enabled, no check mark when disabled.

Dependency decision:

* No new package was added.

Test commands and results:

* `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` returned `40 passed in 0.27s`.

Manual acceptance status:

* Tray menu check mark behavior has been accepted by the user.

## Current Tray Menu Immediate Check Mark Fix

User reported that clicking "开机自启" did not show the check mark ✓ immediately; the menu had to be opened a second time.

Root cause: pystray evaluates `checked` callbacks only when the menu opens, not after an action completes.

Fix:

* Added `TrayIcon.update_menu()` which calls `pystray.Icon.update_menu()` to force rebuild.
* `_toggle_autostart()` and `_toggle_floating_countdown()` in `timer.py` now call `self.tray_icon.update_menu()` after the state change.

Changed files:

* `app/tray.py` — added `update_menu()` method
* `app/timer.py` — call `update_menu()` after each toggle
* `HANDOFF.md`

Test commands and results:

* `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` returned `40 passed in 0.33s`.

Manual acceptance status:

* Immediate check mark update behavior has been accepted by the user.


## Current Idle Detection Feature

User requested that when the user is away from the computer, EyeBreak should stop reminding until the user returns.

Changed files:

* app/config.py
* app/idle.py (new)
* app/timer.py
* app/floating_countdown.py
* config.json
* tests/test_config.py
* tests/test_idle.py (new)
* tests/test_timer.py
* README.md
* HANDOFF.md

Current behavior:

* config.json has a new idle_threshold_minutes field (default 5). Set to 0 to disable idle detection.
* app/idle.py uses ctypes.windll.user32.GetLastInputInfo to detect seconds since last user input.
* In ReminderTimer._tick(), when not paused and idle threshold > 0, if idle >= threshold the timer shows (translated) idle and suppresses reminders. When the user returns, next_reminder_at is reset so the reminder interval restarts from the beginning.
* FloatingCountdownWindow.set_idle() shows idle status in gray (#9ca3af) and dashes countdown.

Dependency decision:

* No new package was added.
* ctypes standard library wraps the Windows GetLastInputInfo API.

Test commands and results:

* python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest returned 44 passed in 0.49s.
* 2 new tests in tests/test_idle.py (non-Windows fallback + real Windows call).
* 1 new config test for idle_threshold_minutes = 0 (disabled).

Manual acceptance status:

* Idle detection behavior has been accepted by the user.

## Current Acceptance Status Update

User confirmed these previously pending items have been accepted:

* autostart toggle behavior;
* PyInstaller build output;
* tray check-mark immediate-refresh behavior.

Changed files:

* `README.md`
* `HANDOFF.md`

Current behavior:

* No code behavior changed in this update.
* Project documentation now marks the three items above as accepted.
* `HANDOFF.md` also fixes corrupted PyInstaller path text from earlier notes.

Dependency decision:

* No dependency changes.

Test impact:

* Tests were not rerun for this documentation-only acceptance update.
* Last confirmed test baseline remains `44 passed` with
  `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` after escalated rerun.

Manual acceptance status:

* Tray settings window behavior has been accepted by the user.

## Current Tray Settings Window Feature

User requested continuing the next development milestone after accepted autostart, PyInstaller build output, and tray check-mark refresh work.

Changed files:

* `app/settings_window.py` (new)
* `app/tray.py`
* `app/timer.py`
* `tests/test_settings_window.py` (new)
* `tests/test_tray.py`
* `tests/test_timer.py`
* `README.md`
* `HANDOFF.md`

Current behavior:

* The tray menu now has a `设置` item.
* Selecting `设置` opens a Tkinter settings window.
* Selecting `设置` again focuses the existing settings window instead of opening duplicates.
* The settings window edits:
  * reminder interval in minutes;
  * break duration in seconds;
  * default pause duration in minutes;
  * idle detection threshold in minutes, where `0` disables idle detection.
* Saving valid settings writes `config.json` through the existing `save_config()` path.
* Saving settings hot-updates the running timer:
  * if not paused, the next reminder countdown restarts with the new interval;
  * if paused, the current pause deadline is preserved and the post-pause reminder time is recalculated with the new interval.
* Invalid settings show a Tkinter error dialog and do not overwrite `config.json`.

Dependency decision:

* No new dependency was added.
* Tkinter is already used by the app and is enough for this settings window.
* No third-party settings package was added because it would increase install/build surface for a small four-field dialog.

Test commands and results:

* Ordinary run: `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` returned `46 passed, 8 errors`; errors were the known Windows sandbox `.tmp\pytest` cleanup `PermissionError: [WinError 5]`, not assertion failures.
* Escalated rerun of the same command passed: `54 passed in 0.33s`.

Manual acceptance status:

* Tray settings window behavior has been accepted by the user.

Known limitations / next work:

* The settings window intentionally does not edit autostart or floating-window toggle because those already have dedicated tray controls.

## Current Settings Window Acceptance Update

User acceptance:

* User confirmed acceptance with: `验收没问题`.

Changed files:

* `README.md`
* `HANDOFF.md`

Current behavior:

* No code behavior changed in this update.
* Documentation now marks the tray settings window behavior as accepted.
* Pending manual acceptance is back to none at this point.

Dependency decision:

* No dependency changes.

Test impact:

* Tests were not rerun for this documentation-only acceptance update.
* Last confirmed full test result remains `54 passed in 0.44s` with `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` after escalated rerun.

Manual acceptance status:

* No pending manual acceptance items are recorded at this point.
## Current Fullscreen Detection Feature

User approved the next planned feature after settings window acceptance.

Changed files:

* `app/config.py`
* `app/fullscreen.py` (new)
* `app/floating_countdown.py`
* `app/settings_window.py`
* `app/timer.py`
* `tests/test_config.py`
* `tests/test_fullscreen.py` (new)
* `tests/test_settings_window.py`
* `tests/test_timer.py`
* `README.md`
* `HANDOFF.md`

Current behavior:

* `AppConfig` now has `fullscreen_detection_enabled`, defaulting to `True`.
* Existing `config.json` files without the new field still load with fullscreen detection enabled.
* The settings window has a `全屏时延后提醒` checkbox.
* `app/fullscreen.py` uses Windows APIs through standard-library `ctypes`:
  * foreground window handle;
  * shell-window exclusion;
  * foreground window rectangle;
  * nearest monitor rectangle;
  * edge comparison with a 2px tolerance.
* On non-Windows or API failure, fullscreen detection returns `False`.
* When fullscreen is active and the feature is enabled:
  * reminder popup is suppressed;
  * floating countdown status changes to `全屏中` in blue;
  * countdown text shows `--:--`.
* When fullscreen exits, EyeBreak restarts the next reminder interval from the beginning.
* Idle detection still takes priority over fullscreen detection.
* Pause still takes priority over idle/fullscreen checks.

Dependency decision:

* No new package was added.
* Python standard-library `ctypes` is enough for foreground-window and monitor detection.
* External Windows GUI packages were rejected because they would increase runtime/build surface for a small platform API wrapper.

Test commands and results:

* Ordinary run: `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` returned `54 passed, 10 errors`; errors were the known Windows sandbox `.tmp\pytest` cleanup `PermissionError: [WinError 5]`, not assertion failures.
* Escalated rerun of the same command passed after final encoding cleanup: `64 passed in 0.40s`.

Manual acceptance status:

* Fullscreen detection behavior has been accepted by the user.

Known limitations / next work:

* Encoding cleanup removed accidental BOM churn from Python files that do not use BOM and kept existing BOM on files that already used it.
* Borderless fullscreen apps are handled when their foreground window covers the monitor rectangle; the current milestone has been manually accepted.

## Current Fullscreen Detection Acceptance Update

User acceptance:

* User confirmed acceptance with: `验收没问题`.

Changed files:

* `README.md`
* `HANDOFF.md`

Current behavior:

* No code behavior changed in this update.
* Documentation now marks fullscreen detection behavior as accepted.
* Pending manual acceptance is back to none at this point.

Dependency decision:

* No dependency changes.

Test impact:

* Tests were not rerun for this documentation-only acceptance update.
* Last confirmed full test result remains `64 passed in 0.40s` with `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` after escalated rerun.

Manual acceptance status:

* No pending manual acceptance items are recorded at this point.
## Current Release Record Feature

User approved adding a lightweight release/version record after accepted fullscreen detection.

Changed files:

* `VERSION` (new)
* `RELEASES.md` (new)
* `HANDOFF.md`

Current behavior:

* `VERSION` records the accepted baseline version as `v1`.
* `RELEASES.md` records the accepted baseline release `v1` dated 2026-07-04.
* The release baseline is explicitly tied to commit `a697c05` on `master`.
* The release record lists included accepted features, build command, test baseline, manual acceptance scope, and excluded work.
* Current local `config.json` edits are explicitly excluded from release `v1`.

Dependency decision:

* No dependency changes.
* Plain Markdown and a plain text `VERSION` file are enough for a lightweight desktop release record.

Test impact:

* Tests were not rerun for this documentation-only release-record change.
* Last confirmed full test result remains `64 passed in 0.40s` with `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` after escalated rerun.

Manual acceptance status:

* Release record has been accepted by the user.

Known limitations / next work:

* Earlier release draft notes excluded the autostart runtime path fix, but that exclusion is no longer current after `a697c05` was submitted.

## Current Release Name Adjustment

User requested the lightweight release name should be `v1` instead of `0.1.0`.

Changed files:

* `VERSION`
* `RELEASES.md`
* `HANDOFF.md`

Current behavior:

* The accepted baseline release is now named `v1`.
* The release now points to commit `a697c05` on `master`.
* No code behavior changed.

Dependency decision:

* No dependency changes.

Test impact:

* Tests were not rerun for this documentation-only rename.
* Last confirmed full test result remains `64 passed in 0.40s` with `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` after escalated rerun.

Manual acceptance status:

* Release name adjustment has been accepted by the user.
## Current Release Record Chinese Rewrite

User requested the release record should be written in Chinese.

Changed files:

* `RELEASES.md`
* `HANDOFF.md`

Current behavior:

* `RELEASES.md` now uses Chinese headings and Chinese release notes.
* Release name remains `v1`.
* Release baseline now remains accepted commit `a697c05` on `master`.
* The release record is Chinese and now includes the submitted autostart runtime path fix through `a697c05`.

Dependency decision:

* No dependency changes.

Test impact:

* Tests were not rerun for this documentation-only rewrite.
* Last confirmed full test result remains `64 passed in 0.40s` with `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` after escalated rerun.

Manual acceptance status:

* Chinese release record has been accepted by the user.

## Current Autostart Runtime Path Fix Accepted

User confirmed acceptance in this turn.

Changed files:

* `README.md`
* `HANDOFF.md`

Current behavior:

* No code behavior changed in this update.
* Documentation now marks the autostart runtime path fix as accepted.

Dependency decision:

* No dependency changes.

Test impact:

* Tests were not rerun for this documentation-only acceptance update.
* Last confirmed full test result remains `73 passed in 0.35s` with `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest`.

Manual acceptance status:

* Autostart runtime path fix has been accepted by the user.
## Current Release Baseline Recheck

User said the autostart runtime path fix has now been submitted. I refreshed `origin/master` with `git fetch origin` and verified local `HEAD` and `origin/master` both point to `a697c05`.

Changed files:

* `RELEASES.md`
* `HANDOFF.md`

Current behavior:

* `RELEASES.md` now uses `a697c05` as the `v1` source baseline.
* `v1` now includes the accepted autostart runtime path fix.
* The old exclusion for autostart runtime path fix work has been removed.
* `v1` still excludes the current local `config.json` change and non-MVP future scope.

Dependency decision:

* No dependency changes.

Test impact:

* Tests were not rerun for this documentation-only release-record correction.
* Last confirmed full test result for the new baseline remains `73 passed in 0.35s` with `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` after escalated rerun.

Manual acceptance status:

* Corrected `v1` release record has been accepted by the user.
## Current v1 Release Record Accepted

User confirmed acceptance with: `验收`.

Changed files:

* `VERSION`
* `RELEASES.md`
* `HANDOFF.md`

Current behavior:

* `VERSION` is `v1`.
* `RELEASES.md` is written in Chinese.
* The `v1` baseline is commit `a697c05` on `master`.
* `v1` includes the accepted autostart runtime path fix.
* Current local `config.json` changes remain excluded from the release record.

Dependency decision:

* No dependency changes.

Test impact:

* Tests were not rerun for this documentation-only acceptance update.
* Last confirmed full test result for the release baseline remains `73 passed in 0.35s` with `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` after escalated rerun.

Manual acceptance status:

* `v1` release record has been accepted by the user.

## 2026-07-04 Repository Hygiene Cleanup

Changed files:

- Removed `config.json` from Git tracking while keeping it as local runtime state.
- Removed `github仓库地址.md`; it only duplicated the remote URL.
- Removed `MVP软件开发.md`; it was an outdated roadmap already superseded by `README.md` and `RELEASES.md`.
- Updated `.gitignore` to ignore local config, runtime state, logs, virtualenvs, coverage output, tool scratch files, and PyInstaller build outputs.
- Updated `README.md` to state that `config.json` is generated on first run and intentionally ignored by Git.

Current behavior:

- First run still creates or repairs `config.json` through the existing config loader.
- The repository now keeps source code, tests, dependencies, app icon, PyInstaller build recipe, release notes, and AI handoff docs.
- Local runtime config remains on the developer machine and is not part of Git commits.

Dependency decisions:

- No dependency added, removed, or upgraded.
- External reference check used GitHub Python `.gitignore` and PyPA project-structure guidance; `build.spec` is intentionally kept because it is this app's accepted PyInstaller build recipe.

Install/run/test impact:

- Fresh clones will not include `config.json`; running `python main.py` creates local config state.
- Build command remains `python -m PyInstaller build.spec`.
- First test run: `python -m pytest -q tests -p no:cacheprovider --basetemp=.tmp\pytest` returned `62 passed, 11 errors`; all errors were Windows sandbox cleanup failures for `.tmp\pytest`.
- Escalated rerun of the same command passed: `73 passed in 0.40s`.

Known failures or limitations:

- Direct `Remove-Item` deletion was blocked by Windows permission handling in the sandbox, so tracked docs were removed with `git rm` instead.
- Ordinary-permission pytest can still fail while cleaning `.tmp\pytest`; escalated pytest passed with no assertion failures.
- The local `config.json` file remains in the working tree as ignored runtime state.
