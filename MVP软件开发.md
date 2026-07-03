# EyeBreak Current Development Roadmap

## Completed Baseline

- Fixed-interval reminder loop.
- Topmost reminder popup.
- 20-second break countdown.
- Skip current reminder.
- Pause reminders.
- Resume reminders.
- Immediate break.
- Exit flow.
- JSON config.
- Countdown status window.
- System tray menu.
- Custom tray/window icon.
- Automated tests for config, timer display, tray, and icon behavior.

## Current Pending Acceptance

- Visual acceptance of the generated tray and window icon on Windows.

## Next Milestone: Edge-Docked Floating Countdown

Goal:

Replace the simple countdown status window with an edge-docked auto-hide floating
countdown display.

Requirements:

- Show time until the next reminder.
- Stay mostly hidden at the screen edge by default.
- Reveal when the mouse pointer touches or hovers over the visible tab.
- Auto-hide after the pointer leaves or after a short delay.
- Avoid stealing focus.
- Support one predictable edge position first.
- Do not add multi-edge customization in the first version.

Acceptance:

- Floating tab appears at the screen edge.
- It does not block normal work.
- Hovering reveals the countdown.
- Leaving the area hides it again.
- Countdown remains accurate during normal countdown and pause.
- Pause state displays clearly.
- Reminder popup still appears correctly.
- Tray menu still works.
- Exit still fully terminates the app.

## Later Milestones

1. Package as exe.
2. Add startup integration.
3. Add idle detection.
4. Add fullscreen detection.
5. Add simple daily statistics.
6. Consider integration into Screen-Time-Management only after standalone use is stable.