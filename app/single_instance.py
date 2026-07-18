"""Windows single-instance coordination for the EyeBreak desktop app."""

from __future__ import annotations

import ctypes
import time
from collections.abc import Callable
from ctypes import wintypes


MUTEX_NAME = r"Local\EyeBreak.SingleInstance"
ACTIVATION_EVENT_NAME = r"Local\EyeBreak.ActivateExistingSession"
ERROR_ALREADY_EXISTS = 183
EVENT_MODIFY_STATE = 0x0002
WAIT_OBJECT_0 = 0
WAIT_TIMEOUT = 258


class SingleInstanceManager:
    """Own the primary process slot or activate the process that already does."""

    def __init__(
        self,
        kernel32=None,
        sleep: Callable[[float], None] = time.sleep,
        activation_retries: int = 10,
        activation_retry_seconds: float = 0.05,
    ) -> None:
        self._kernel32 = kernel32 or _load_kernel32()
        self._sleep = sleep
        self._activation_retries = activation_retries
        self._activation_retry_seconds = activation_retry_seconds
        self._mutex_handle = None
        self._activation_event_handle = None

    def acquire_or_activate(self) -> bool:
        """Return ``True`` for the primary instance, otherwise signal and exit."""
        mutex_handle = self._kernel32.CreateMutexW(None, False, MUTEX_NAME)
        if not mutex_handle:
            raise ctypes.WinError(ctypes.get_last_error())

        if self._kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            self._close_handle(mutex_handle)
            self._signal_existing_instance()
            return False

        self._mutex_handle = mutex_handle
        event_handle = self._kernel32.CreateEventW(
            None, False, False, ACTIVATION_EVENT_NAME
        )
        if not event_handle:
            error = ctypes.get_last_error()
            self.close()
            raise ctypes.WinError(error)

        self._activation_event_handle = event_handle
        return True

    def consume_activation_request(self) -> bool:
        """Return whether another launch asked the primary instance to activate."""
        if not self._activation_event_handle:
            return False
        result = self._kernel32.WaitForSingleObject(self._activation_event_handle, 0)
        if result == WAIT_OBJECT_0:
            return True
        if result == WAIT_TIMEOUT:
            return False
        raise ctypes.WinError(ctypes.get_last_error())

    def close(self) -> None:
        """Release primary-instance handles. Safe to call multiple times."""
        self._close_handle(self._activation_event_handle)
        self._activation_event_handle = None
        self._close_handle(self._mutex_handle)
        self._mutex_handle = None

    def _signal_existing_instance(self) -> bool:
        for attempt in range(self._activation_retries):
            event_handle = self._kernel32.OpenEventW(
                EVENT_MODIFY_STATE, False, ACTIVATION_EVENT_NAME
            )
            if event_handle:
                try:
                    return bool(self._kernel32.SetEvent(event_handle))
                finally:
                    self._close_handle(event_handle)
            if attempt < self._activation_retries - 1:
                self._sleep(self._activation_retry_seconds)
        return False

    def _close_handle(self, handle) -> None:
        if handle:
            self._kernel32.CloseHandle(handle)


def _load_kernel32():
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.CreateEventW.argtypes = (
        wintypes.LPVOID, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR
    )
    kernel32.CreateEventW.restype = wintypes.HANDLE
    kernel32.OpenEventW.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR)
    kernel32.OpenEventW.restype = wintypes.HANDLE
    kernel32.SetEvent.argtypes = (wintypes.HANDLE,)
    kernel32.SetEvent.restype = wintypes.BOOL
    kernel32.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
    kernel32.WaitForSingleObject.restype = wintypes.DWORD
    kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.GetLastError.argtypes = ()
    kernel32.GetLastError.restype = wintypes.DWORD
    return kernel32
