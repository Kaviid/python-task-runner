# Python Task Runner

A configurable **task runner** that executes Python scripts, retries on failure, and logs errors with full tracebacks.  
Designed as a practical real-world project using Python’s standard library modules (`sys`, `pathlib`, `runpy`, `functools`, `traceback`, `datetime`, and decorators).

---

## ✨ Features
- Run external Python scripts listed in a config file
- Retry failed tasks with a custom `@retry` decorator
- Capture and log full error tracebacks
- Store logs in timestamped files
- Print a clean summary report with success/failure and runtime
- Built only with Python standard library (no external deps)

---
