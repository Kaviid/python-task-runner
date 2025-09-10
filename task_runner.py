#!/usr/bin/env python3
"""
Automated Task Runner with Logging & Config
Spec: PY-REALWORLD-001

Features
- Reads tasks.json (relative to this file) and runs only enabled tasks.
- CLI: `python task_runner.py all` or `python task_runner.py <task_name>`
- Per-task logging (START/SUCCESS/FAIL), timestamps, durations.
- Traceback captured on failure; automatic retries (default 2).
- Proper exit codes: 0 if all requested tasks succeed; 1 otherwise.
- Strictly uses paths relative to this file (works from any CWD).
"""

from __future__ import annotations
#Python has a special module called __future__ 
#It lets you use features from newer versions of Python before they’re the default.
#Basically, it’s a “turn this new behavior on now” switch.

import sys
import json
import time
import traceback
import functools
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict

# --------------------------------------------------------------------------------------
# Paths & logging setup (relative to this file)
# --------------------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "runner.log"

CONFIG_PATH = SCRIPT_DIR / "tasks.json" #.json file path

def append_log(text: str) -> None:
    """Append a line (or lines) to the runner log."""
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(text)


def ts() -> str:
    """Timestamp string for log lines."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# --------------------------------------------------------------------------------------
# Decorator: logging + retry wrapper
# --------------------------------------------------------------------------------------

def with_logging_and_retry(max_retries: int = 2) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """
    Decorator that:
      - logs START/SUCCESS/FAIL with timestamps and durations,
      - captures and logs full traceback on failure,
      - retries the function up to `max_retries` times (so attempts = max_retries + 1).
    """
    def decorator(func: Callable[..., object]) -> Callable[..., object]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts <= max_retries:
                start_label = ts()
                t0 = time.perf_counter()
                try:
                    print(f"[{start_label}] START {func.__name__}")
                    result = func(*args, **kwargs)
                    dt = time.perf_counter() - t0
                    append_log(f"[{start_label}] SUCCESS {func.__name__} in {dt:.3f}s\n")
                    return result
                except Exception:
                    dt = time.perf_counter() - t0
                    tb = traceback.format_exc()
                    append_log(f"[{start_label}] FAIL {func.__name__} in {dt:.3f}s\n{tb}\n")
                    attempts += 1
                    if attempts <= max_retries:
                        retry_label = ts()
                        msg = f"[{retry_label}] Retrying {func.__name__}... ({attempts}/{max_retries})\n"
                        print(msg.strip())
                        append_log(msg)
                    else:
                        # Final failure: re-raise so caller can mark overall exit code
                        raise
        return wrapper
    return decorator


# --------------------------------------------------------------------------------------
# Example task functions (dummy implementations)
# One intentionally fails to exercise retry + traceback logging.
# --------------------------------------------------------------------------------------

@with_logging_and_retry(max_retries=2)
def daily_backup() -> None:
    """
    Pretend to back up files somewhere.
    Replace print with real work in a real project.
    """
    # Simulated work
    time.sleep(0.3)
    print("daily_backup: Backup completed.")


@with_logging_and_retry(max_retries=2)
def generate_report() -> None:
    """
    Pretend to generate a report.
    """
    time.sleep(0.25)
    print("generate_report: Report generated.")


@with_logging_and_retry(max_retries=2)
def send_email() -> None:
    """
    Intentionally fail to test retry + traceback logging.
    Comment out the exception if you want it to pass.
    """
    time.sleep(0.2)
    # Intentionally failing to validate retries/traceback logging:
    raise ValueError("Email server not reachable (intentional test failure).")
    # print("send_email: Email sent.")  # <- enable this and comment the raise to make it pass.


# --------------------------------------------------------------------------------------
# TASKS mapping: string name -> function object
# --------------------------------------------------------------------------------------

TASKS: Dict[str, Callable[[], None]] = {
    "daily_backup": daily_backup,
    "generate_report": generate_report,
    "send_email": send_email,
}


# --------------------------------------------------------------------------------------
# Config loading & enabled-task filtering
# --------------------------------------------------------------------------------------

def load_config(path: Path) -> dict:
    if not path.exists():
        print(f"[ERROR] Missing config file: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def get_enabled_task_names(cfg: dict) -> list[str]:
    """
    Expect a JSON shape:
      { "tasks": [ {"name": "daily_backup", "enabled": true}, ... ] }
    Returns a list of task names that are enabled AND defined in TASKS.
    Warns if config enables an undefined task.
    """
    enabled: list[str] = []
    items = cfg.get("tasks", [])
    if not isinstance(items, list):
        print("[ERROR] `tasks` must be a list in tasks.json", file=sys.stderr)
        sys.exit(1)

    for item in items:
        if not isinstance(item, dict):
            print("[WARN] Skipping malformed task entry (not an object).", file=sys.stderr)
            continue
        name = item.get("name")
        enabled_flag = bool(item.get("enabled"))
        if not name or not enabled_flag:
            continue
        if name in TASKS:
            enabled.append(name)
        else:
            print(f"[WARN] Task '{name}' is enabled in config but not defined in code.", file=sys.stderr)
    return enabled


# --------------------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------------------

def run_tasks(request: str, enabled_names: list[str]) -> int:
    """
    Run `all` enabled tasks or one specific task.
    Returns exit code: 0 if all requested succeeded, 1 otherwise.
    """
    append_log(f"\n=== Session {ts()} ===\n")
    append_log(f"Requested: {request}\n")

    had_failure = False

    if request == "all":
        # Preserve enabled order as in config
        for name in enabled_names:
            func = TASKS.get(name)
            if not func:
                # Shouldn't happen due to pre-filtering, but guard anyway
                print(f"[ERROR] Task '{name}' not found in TASKS.", file=sys.stderr)
                append_log(f"[{ts()}] ERROR Task '{name}' missing in TASKS\n")
                had_failure = True
                continue
            try:
                func()  # wrapped by decorator for logging + retries
            except Exception:
                had_failure = True
    else:
        # Single task mode
        if request not in enabled_names:
            # Clear message showing what *is* allowed right now
            enabled_str = ", ".join(enabled_names) if enabled_names else "(none enabled)"
            print(f"[ERROR] Task '{request}' is not enabled or not defined.\n"
                  f"Enabled tasks right now: {enabled_str}", file=sys.stderr)
            append_log(f"[{ts()}] ERROR Requested '{request}' not enabled/defined\n")
            return 1
        func = TASKS.get(request)
        if not func:
            print(f"[ERROR] Task '{request}' not found in TASKS.", file=sys.stderr)
            append_log(f"[{ts()}] ERROR Task '{request}' missing in TASKS\n")
            return 1
        try:
            func()
        except Exception:
            had_failure = True

    append_log(f"=== End Session (fail={had_failure}) ===\n")
    return 1 if had_failure else 0


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python task_runner.py [all|<task_name>]", file=sys.stderr)
        return 1

    request = argv[1].strip()
    cfg = load_config(CONFIG_PATH)
    enabled_names = get_enabled_task_names(cfg)

    if request != "all" and request not in enabled_names:
        # we’ll let run_tasks re-check and print a nice message, but short-circuiting here is also fine
        pass

    print("Starting Task Runner...\n")
    return run_tasks(request, enabled_names)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
