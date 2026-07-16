"""EyeBreak — 护眼休息提醒工具。

Entry point with dependency-injection wiring (Phase 4 architecture).
Replaces the old God-class ReminderTimer with an event-driven pipeline:

    Config/State load
        → EventBus + StateMachine
        → Platform adapters
        → TimerEngine (pure business logic)
        → EyeBreakBridge (UI wiring)
        → tkinter mainloop
"""

import tkinter as tk

from app.config import load_config
from app.core.event_bus import EventBus
from app.core.state_machine import StateMachine
from app.core.timer_engine import TimerEngine
from app.platform.adapters import (
    AutostartManagerAdapter,
    FullscreenDetectorAdapter,
    IdleDetectorAdapter,
)
from app.state import load_app_state
from app.ui.bridge import EyeBreakBridge


def main() -> None:
    # ── Infrastructure ──────────────────────────────────────────
    bus = EventBus()
    sm = StateMachine(bus)

    # ── Platform adapters ───────────────────────────────────────
    idle_detector = IdleDetectorAdapter()
    fullscreen_detector = FullscreenDetectorAdapter()
    autostart_manager = AutostartManagerAdapter()

    # ── Persistence ─────────────────────────────────────────────
    config = load_config()
    state = load_app_state()

    # ── Core engine ─────────────────────────────────────────────
    engine = TimerEngine(
        bus=bus,
        state_machine=sm,
        idle_detector=idle_detector,
        fullscreen_detector=fullscreen_detector,
        autostart_manager=autostart_manager,
        config=config,
        state=state,
    )

    # ── UI ──────────────────────────────────────────────────────
    root = tk.Tk()
    root.withdraw()  # hide the root window — the floating window and tray are the UI

    bridge = EyeBreakBridge(
        root=root,
        bus=bus,
        engine=engine,
        state=state,
        autostart_manager=autostart_manager,
    )
    bridge.build()

    root.mainloop()


if __name__ == "__main__":
    main()