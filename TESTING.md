# Testing

Durable record of what's been manually verified, by phase. Automated test
suites (if/when they exist) belong in `tests/` and run via CI; this file is
for things that currently require a human on a real machine — starting with
Phase 1, which drives a live Windows desktop and can't run in headless CI.

Each entry: Test ID, preconditions, steps, expected vs. actual result,
status, date, evidence. Only the current result for each test lives here —
history of prior runs is in git log for this file, not duplicated inline.

## Phase 1 — Automation driver (`src/automation/driver.py`)

Environment: Windows 10/11, Python 3.10+, installed via `install.bat`.

### P1-01 — Clean install
- **Preconditions:** no `.venv/` present (delete if left over from a prior run).
- **Steps:** double-click `install.bat`.
- **Expected:** script reaches `=== Setup complete ===` with no `Write-Error`
  lines; smoke test prints real window titles from the desktop under
  "Open windows:".
- **Status:** Pass
- **Date:** 2026-11-03
- **Evidence:** —

### P1-02 — `list_open_windows()` sanity
- **Preconditions:** Notepad (or any simple app) open.
- **Steps:** `python -c "from src.automation.driver import list_open_windows; print(list_open_windows())"`
- **Expected:** Notepad's exact title string appears in the list.
- **Status:** Not yet run — pending
- **Date:** —
- **Evidence:** —

### P1-03 — Scoped `attach_or_launch`
- **Preconditions:** Notepad open with a known exact title.
- **Steps:**
  ```python
  from src.automation import AutomationDriver
  d = AutomationDriver(app_title="Untitled - Notepad")
  d.attach_or_launch()
  ```
  Then construct with a title that doesn't exist and no `launch_command`.
- **Expected:** Notepad gets focus, no exception. The nonexistent-title case
  raises a clean `RuntimeError`, not a crash.
- **Status:** Not yet run — pending
- **Date:** —
- **Evidence:** —

### P1-04 — Window-scoped click + type
- **Steps:** `d.type_text("hello phase 1")`, then `d.click(10, 10)`, then
  `d.click(999999, 999999)`.
- **Expected:** typed text lands inside the target window regardless of
  current focus elsewhere; in-bounds click succeeds; out-of-bounds click
  raises `ValueError`, doesn't click somewhere unintended.
- **Status:** Not yet run — pending
- **Date:** —
- **Evidence:** —

### P1-05 — Panic stop #1 (`request_abort()`)
- **Steps:** start a long `type_text(...)` call; call `d.request_abort()`
  from another thread mid-typing.
- **Expected:** `PanicStopError` raised; typing stops within one chunk, not
  after the full string.
- **Status:** Not yet run — pending
- **Date:** —
- **Evidence:** —

### P1-06 — Panic stop #2 (PyAutoGUI `FAILSAFE`)
- **Steps:** trigger a `click()`/mouse move, yank the mouse to a screen
  corner mid-motion.
- **Expected:** `pyautogui.FailSafeException` raised, action aborted.
- **Status:** Not yet run — pending
- **Date:** —
- **Evidence:** —

### P1-07 — Multi-window ambiguity guard
- **Preconditions:** two windows open with the identical exact title.
- **Steps:** `attach_or_launch()` against that shared title.
- **Expected:** `RuntimeError` naming the ambiguity; does not silently pick
  one of the matches.
- **Status:** Not yet run — pending
- **Date:** —
- **Evidence:** —

Phase 1 is complete once P1-01 through P1-07 all show **Pass** with a date
and evidence filled in.
