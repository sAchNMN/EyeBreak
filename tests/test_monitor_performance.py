from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from scripts.monitor_performance import (
    Sample,
    build_parser,
    calculate_cpu_percent,
    summarize_samples,
    write_samples_csv,
)


def test_calculate_cpu_percent_normalizes_process_time_across_cpus() -> None:
    # 0.2 seconds of process time over 1 second on a 4-CPU machine is 5%.
    assert calculate_cpu_percent(2_000_000, 1.0, 4) == 5.0


def test_summarize_samples_reports_cpu_and_memory_trend() -> None:
    samples = [
        Sample(elapsed_seconds=0.0, cpu_percent=0.0, rss_bytes=10 * 1024 * 1024),
        Sample(elapsed_seconds=5.0, cpu_percent=2.0, rss_bytes=11 * 1024 * 1024),
        Sample(elapsed_seconds=10.0, cpu_percent=4.0, rss_bytes=13 * 1024 * 1024),
    ]

    assert summarize_samples(samples) == {
        "sample_count": 3,
        "cpu_average_percent": 2.0,
        "cpu_p95_percent": 4.0,
        "cpu_max_percent": 4.0,
        "rss_initial_mb": 10.0,
        "rss_final_mb": 13.0,
        "rss_peak_mb": 13.0,
        "rss_delta_mb": 3.0,
    }


def test_write_samples_csv_preserves_measurements(tmp_path) -> None:
    output = tmp_path / "performance.csv"
    samples = [Sample(elapsed_seconds=5.0, cpu_percent=1.25, rss_bytes=12 * 1024 * 1024)]

    write_samples_csv(output, samples)

    with output.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    assert rows == [
        {
            "elapsed_seconds": "5.0",
            "cpu_percent": "1.25",
            "rss_mb": "12.0",
        }
    ]


def test_parser_does_not_pass_command_separator_to_process() -> None:
    args = build_parser().parse_args(["--", "py", "main.py"])

    assert args.command == ["py", "main.py"]


def test_monitor_stops_when_target_process_exits(tmp_path) -> None:
    if sys.platform != "win32":
        return  # skip on non-Windows; Win32 process APIs are unavailable

    script = Path(__file__).resolve().parents[1] / "scripts" / "monitor_performance.py"
    output = tmp_path / "process-exit.csv"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--duration",
            "2",
            "--interval",
            "0.1",
            "--output",
            str(output),
            "--",
            sys.executable,
            "-c",
            "import time; time.sleep(0.3)",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "监测提前结束" in result.stderr
    with output.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert float(rows[-1]["elapsed_seconds"]) < 1.0
