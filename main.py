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
from app.single_instance import SingleInstanceManager
from app.state import load_app_state
from app.ui.bridge import EyeBreakBridge


def main() -> None:
    single_instance = SingleInstanceManager()
    if not single_instance.acquire_or_activate():
        return

    try:
        _run_primary_instance(single_instance)
    finally:
        single_instance.close()


def _run_primary_instance(single_instance: SingleInstanceManager) -> None:
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
    _poll_activation_requests(root, bridge, single_instance)
    root.mainloop()


def _poll_activation_requests(
    root: tk.Tk,
    bridge: EyeBreakBridge,
    single_instance: SingleInstanceManager,
) -> None:
    """Handle activation signals on Tk's UI thread without a worker thread."""
    if bridge.engine.is_terminal:
        return
    if single_instance.consume_activation_request():
        bridge.activate_existing_session()
    root.after(250, _poll_activation_requests, root, bridge, single_instance)

if __name__ == "__main__":
    main()