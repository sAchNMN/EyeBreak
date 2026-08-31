"""Measure CPU and resident memory usage of a Windows process."""

from __future__ import annotations

import argparse
import csv
import ctypes
import math
import os
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TextIO

from ctypes import wintypes


PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
PROCESS_ACCESS = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
STILL_ACTIVE = 259
CSV_FIELDS = ("elapsed_seconds", "cpu_percent", "rss_mb")


class FILETIME(ctypes.Structure):
    _fields_ = [
        ("dwLowDateTime", wintypes.DWORD),
        ("dwHighDateTime", wintypes.DWORD),
    ]


class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


@dataclass(frozen=True)
class Sample:
    elapsed_seconds: float
    cpu_percent: float
    rss_bytes: int


def calculate_cpu_percent(
    process_time_delta_100ns: int,
    elapsed_seconds: float,
    cpu_count: int,
) -> float:
    """Return process CPU usage normalized to all logical CPUs."""
    if process_time_delta_100ns <= 0 or elapsed_seconds <= 0:
        return 0.0

    elapsed_process_seconds = process_time_delta_100ns / 10_000_000
    return min(
        100.0,
        elapsed_process_seconds / elapsed_seconds / max(1, cpu_count) * 100,
    )


def summarize_samples(samples: list[Sample]) -> dict[str, float | int]:
    """Summarize CPU usage and RSS change for collected samples."""
    if not samples:
        return {
            "sample_count": 0,
            "cpu_average_percent": 0.0,
            "cpu_p95_percent": 0.0,
            "cpu_max_percent": 0.0,
            "rss_initial_mb": 0.0,
            "rss_final_mb": 0.0,
            "rss_peak_mb": 0.0,
            "rss_delta_mb": 0.0,
        }

    cpu_values = [sample.cpu_percent for sample in samples]
    rss_values = [sample.rss_bytes for sample in samples]
    return {
        "sample_count": len(samples),
        "cpu_average_percent": round(statistics.fmean(cpu_values), 2),
        "cpu_p95_percent": round(_percentile(cpu_values, 0.95), 2),
        "cpu_max_percent": round(max(cpu_values), 2),
        "rss_initial_mb": _megabytes(rss_values[0]),
        "rss_final_mb": _megabytes(rss_values[-1]),
        "rss_peak_mb": _megabytes(max(rss_values)),
        "rss_delta_mb": _megabytes(rss_values[-1] - rss_values[0]),
    }


def write_samples_csv(path: Path, samples: list[Sample]) -> None:
    """Write samples to a CSV file for later comparison."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for sample in samples:
            _write_sample(writer, sample)


class ProcessSampler:
    """Read CPU time and working-set memory from a Windows process."""

    def __init__(self, pid: int) -> None:
        if sys.platform != "win32":
            raise RuntimeError("This monitor only supports Windows.")

        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._psapi = ctypes.WinDLL("psapi", use_last_error=True)
        self._configure_api()
        self._pid = pid
        self._handle = self._kernel32.OpenProcess(PROCESS_ACCESS, False, pid)
        if not self._handle:
            raise ctypes.WinError(ctypes.get_last_error())

        try:
            self._last_cpu_time = self._read_cpu_time()
            self._last_sample_time = time.monotonic()
        except Exception:
            self.close()
            raise

    def initial_sample(self) -> Sample:
        self._ensure_running()
        return Sample(0.0, 0.0, self._read_rss_bytes())

    def sample(self, elapsed_seconds: float) -> Sample:
        self._ensure_running()
        now = time.monotonic()
        cpu_time = self._read_cpu_time()
        rss_bytes = self._read_rss_bytes()
        cpu_percent = calculate_cpu_percent(
            cpu_time - self._last_cpu_time,
            now - self._last_sample_time,
            os.cpu_count() or 1,
        )
        self._last_cpu_time = cpu_time
        self._last_sample_time = now
        return Sample(elapsed_seconds, cpu_percent, rss_bytes)

    def close(self) -> None:
        handle = getattr(self, "_handle", None)
        if handle:
            self._kernel32.CloseHandle(handle)
            self._handle = None

    def _configure_api(self) -> None:
        self._kernel32.OpenProcess.argtypes = (
            wintypes.DWORD,
            wintypes.BOOL,
            wintypes.DWORD,
        )
        self._kernel32.OpenProcess.restype = wintypes.HANDLE
        self._kernel32.GetProcessTimes.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(FILETIME),
            ctypes.POINTER(FILETIME),
            ctypes.POINTER(FILETIME),
            ctypes.POINTER(FILETIME),
        )
        self._kernel32.GetProcessTimes.restype = wintypes.BOOL
        self._kernel32.GetExitCodeProcess.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(wintypes.DWORD),
        )
        self._kernel32.GetExitCodeProcess.restype = wintypes.BOOL
        self._kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        self._kernel32.CloseHandle.restype = wintypes.BOOL
        self._get_process_memory_info = self._psapi.GetProcessMemoryInfo
        self._get_process_memory_info.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
            wintypes.DWORD,
        )
        self._get_process_memory_info.restype = wintypes.BOOL

    def _read_cpu_time(self) -> int:
        creation = FILETIME()
        exit_time = FILETIME()
        kernel = FILETIME()
        user = FILETIME()
        if not self._kernel32.GetProcessTimes(
            self._handle,
            ctypes.byref(creation),
            ctypes.byref(exit_time),
            ctypes.byref(kernel),
            ctypes.byref(user),
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        return _filetime_to_int(kernel) + _filetime_to_int(user)

    def _ensure_running(self) -> None:
        exit_code = wintypes.DWORD()
        if not self._kernel32.GetExitCodeProcess(
            self._handle,
            ctypes.byref(exit_code),
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        if exit_code.value != STILL_ACTIVE:
            raise ProcessLookupError(self._pid, "process has exited")

    def _read_rss_bytes(self) -> int:
        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(counters)
        if not self._get_process_memory_info(
            self._handle,
            ctypes.byref(counters),
            counters.cb,
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(counters.WorkingSetSize)


def monitor_process(
    pid: int,
    duration_seconds: float,
    interval_seconds: float,
    output: Path,
) -> list[Sample]:
    """Monitor *pid*, flushing every sample to *output* as it arrives."""
    if duration_seconds <= 0:
        raise ValueError("duration must be greater than zero")
    if interval_seconds <= 0:
        raise ValueError("interval must be greater than zero")

    output.parent.mkdir(parents=True, exist_ok=True)
    samples: list[Sample] = []
    start = time.monotonic()
    sampler = ProcessSampler(pid)
    try:
        with output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
            writer.writeheader()
            initial = sampler.initial_sample()
            samples.append(initial)
            _write_sample(writer, initial)
            stream.flush()
            _print_sample(initial)

            while True:
                elapsed = time.monotonic() - start
                remaining = duration_seconds - elapsed
                if remaining <= 0:
                    break
                time.sleep(min(interval_seconds, remaining))
                elapsed = time.monotonic() - start
                try:
                    current = sampler.sample(elapsed)
                except OSError as error:
                    print(f"无法继续读取进程，监测提前结束：{error}", file=sys.stderr)
                    break
                samples.append(current)
                _write_sample(writer, current)
                stream.flush()
                _print_sample(current)
    finally:
        sampler.close()
    return samples


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Monitor a Windows process CPU usage and RSS/working-set memory."
    )
    parser.add_argument("--pid", type=int, help="PID of an already running process")
    parser.add_argument(
        "--duration",
        type=float,
        default=600.0,
        help="monitoring duration in seconds (default: 600)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="sampling interval in seconds (default: 5)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".tmp") / "performance.csv",
        help="CSV output path (default: .tmp\\performance.csv)",
    )
    parser.add_argument(
        "command",
        nargs="*",
        help="command to start and monitor; put -- before the command",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    if sys.platform != "win32":
        print("此脚本只支持 Windows。", file=sys.stderr)
        return 1

    parser = build_parser()
    args = parser.parse_args(argv)
    if args.pid is not None and args.command:
        parser.error("--pid 和启动命令只能二选一")
    if args.pid is None and not args.command:
        parser.error("请提供 --pid，或使用 -- 后跟要启动的命令")

    process = None
    pid = args.pid
    if pid is None:
        process = subprocess.Popen(args.command)
        pid = process.pid
        print(f"已启动 PID {pid}：{' '.join(args.command)}")

    try:
        samples = monitor_process(pid, args.duration, args.interval, args.output)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"监测失败：{error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("已中断监测；当前已写入的 CSV 数据会保留。", file=sys.stderr)
        return 130

    summary = summarize_samples(samples)
    print(f"CSV：{args.output}")
    print(f"样本数：{summary['sample_count']}")
    print(
        "CPU：平均 {0:.2f}%，P95 {1:.2f}%，峰值 {2:.2f}%".format(
            summary["cpu_average_percent"],
            summary["cpu_p95_percent"],
            summary["cpu_max_percent"],
        )
    )
    print(
        "RSS/工作集：初始 {0:.2f} MB，最终 {1:.2f} MB，峰值 {2:.2f} MB，变化 {3:+.2f} MB".format(
            summary["rss_initial_mb"],
            summary["rss_final_mb"],
            summary["rss_peak_mb"],
            summary["rss_delta_mb"],
        )
    )
    if process is not None and process.poll() is None:
        print(f"被监测进程 PID {process.pid} 仍在运行，脚本不会自动关闭它。")
    return 0


def _filetime_to_int(value: FILETIME) -> int:
    return (value.dwHighDateTime << 32) | value.dwLowDateTime


def _megabytes(byte_count: int) -> float:
    return round(byte_count / (1024 * 1024), 2)


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, math.ceil((len(ordered) - 1) * fraction))
    return ordered[index]


def _sample_row(sample: Sample) -> dict[str, str]:
    return {
        "elapsed_seconds": str(float(sample.elapsed_seconds)),
        "cpu_percent": str(float(sample.cpu_percent)),
        "rss_mb": str(_megabytes(sample.rss_bytes)),
    }


def _write_sample(writer: csv.DictWriter, sample: Sample) -> None:
    writer.writerow(_sample_row(sample))


def _print_sample(sample: Sample) -> None:
    recorded_at = datetime.now().strftime("%H:%M:%S")
    print(
        f"[{recorded_at}] elapsed={sample.elapsed_seconds:.1f}s "
        f"CPU={sample.cpu_percent:.2f}% RSS={_megabytes(sample.rss_bytes):.2f}MB",
        flush=True,
    )


if __name__ == "__main__":
    raise SystemExit(main())
