from __future__ import annotations

from app.single_instance import (
    ERROR_ALREADY_EXISTS,
    WAIT_OBJECT_0,
    WAIT_TIMEOUT,
    SingleInstanceManager,
)


class FakeKernel32:
    def __init__(self, event_open_failures: int = 0) -> None:
        self.last_error = 0
        self.mutex_handles = 0
        self.event_handles = 0
        self.event_signaled = False
        self.event_open_failures = event_open_failures
        self.open_event_calls = 0
        self.closed_handles: list[str] = []

    def CreateMutexW(self, _security, _owner, _name):
        self.last_error = ERROR_ALREADY_EXISTS if self.mutex_handles else 0
        self.mutex_handles += 1
        return f"mutex-{self.mutex_handles}"

    def CreateEventW(self, _security, _manual_reset, _initial_state, _name):
        self.event_handles += 1
        return f"event-primary-{self.event_handles}"

    def OpenEventW(self, _access, _inherit, _name):
        self.open_event_calls += 1
        if self.event_open_failures:
            self.event_open_failures -= 1
            return None
        if not self.event_handles:
            return None
        self.event_handles += 1
        return f"event-secondary-{self.event_handles}"

    def SetEvent(self, _handle):
        self.event_signaled = True
        return True

    def WaitForSingleObject(self, _handle, _timeout):
        if self.event_signaled:
            self.event_signaled = False
            return WAIT_OBJECT_0
        return WAIT_TIMEOUT

    def CloseHandle(self, handle):
        self.closed_handles.append(handle)
        if handle.startswith("mutex-"):
            self.mutex_handles -= 1
        elif handle.startswith("event-"):
            self.event_handles -= 1
        return True

    def GetLastError(self):
        return self.last_error


def test_first_instance_owns_slot_and_second_instance_activates_it() -> None:
    kernel32 = FakeKernel32()
    primary = SingleInstanceManager(kernel32=kernel32)
    secondary = SingleInstanceManager(kernel32=kernel32)

    assert primary.acquire_or_activate() is True
    assert secondary.acquire_or_activate() is False
    assert primary.consume_activation_request() is True
    assert primary.consume_activation_request() is False

    primary.close()
    assert kernel32.mutex_handles == 0
    assert kernel32.event_handles == 0


def test_second_instance_retries_until_primary_event_is_available() -> None:
    sleeps: list[float] = []
    kernel32 = FakeKernel32(event_open_failures=2)
    primary = SingleInstanceManager(kernel32=kernel32)
    secondary = SingleInstanceManager(
        kernel32=kernel32,
        sleep=sleeps.append,
        activation_retry_seconds=0.01,
    )

    assert primary.acquire_or_activate() is True
    assert secondary.acquire_or_activate() is False
    assert kernel32.open_event_calls == 3
    assert sleeps == [0.01, 0.01]
    assert primary.consume_activation_request() is True


def test_closed_primary_slot_can_be_acquired_again() -> None:
    kernel32 = FakeKernel32()
    first = SingleInstanceManager(kernel32=kernel32)

    assert first.acquire_or_activate() is True
    first.close()

    replacement = SingleInstanceManager(kernel32=kernel32)
    assert replacement.acquire_or_activate() is True



def test_activation_poll_opens_existing_session_settings() -> None:
    from unittest.mock import MagicMock

    from main import _poll_activation_requests

    root = MagicMock()
    bridge = MagicMock()
    bridge.engine.is_terminal = False
    single_instance = MagicMock()
    single_instance.consume_activation_request.return_value = True

    _poll_activation_requests(root, bridge, single_instance)

    bridge.activate_existing_session.assert_called_once_with()
    root.after.assert_called_once_with(
        250, _poll_activation_requests, root, bridge, single_instance
    )
