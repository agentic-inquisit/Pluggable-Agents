import subprocess
import sys
import threading
import time

import pyautogui
import pygetwindow as gw
from PIL import Image

if sys.platform != "win32":
    raise RuntimeError(
        "AutomationDriver is Windows-only. Run this on a real Windows machine — "
        "it will not work in this Linux devcontainer."
    )

pyautogui.FAILSAFE = True  # moving mouse to a screen corner aborts the current action


class PanicStopError(RuntimeError):
    """Raised when request_abort() was called — e.g. the user clicked the
    on-screen character to halt the agent. Not a bug; a deliberate stop.
    """


def list_open_windows() -> list[str]:
    """Titles of all currently open windows. Use this to pick the exact
    title to pass as AutomationDriver(app_title=...) — don't guess a
    substring, since window-title matching elsewhere is exact-match only.
    """
    return [title for title in gw.getAllTitles() if title.strip()]


class AutomationDriver:
    """Real Windows automation, scoped to a single assigned application.

    Every action operates within that app's window only — clicks and typed
    text cannot reach outside the window's bounds, and screenshots capture
    only that window's region, not the full desktop. This driver does not
    have general control of the PC; it controls one app you assign it to.
    """

    def __init__(self, app_title: str, launch_command: str | None = None):
        self.app_title = app_title
        self.launch_command = launch_command
        self._window = None
        self._abort_event = threading.Event()

    def request_abort(self) -> None:
        """Panic stop. Wire this to the on-screen character's click handler
        once the overlay (Phase 3) exists — clicking the character should
        call this directly. Safe to call from any thread, at any time.
        """
        self._abort_event.set()

    def reset_abort(self) -> None:
        """Clear a prior abort so the driver can take new actions again."""
        self._abort_event.clear()

    def is_abort_requested(self) -> bool:
        return self._abort_event.is_set()

    def _check_abort(self) -> None:
        if self._abort_event.is_set():
            raise PanicStopError(
                f"Panic stop triggered — aborting action on '{self.app_title}'."
            )

    def attach_or_launch(self, timeout: float = 10.0) -> None:
        """Find the already-open target window, or launch it via
        launch_command and wait for its window to appear.
        """
        window = self._find_window()
        if window is not None:
            self._window = window
            self._window.activate()
            return

        if self.launch_command is None:
            raise RuntimeError(
                f"No window matching '{self.app_title}' is open, and no "
                "launch_command was given to start it."
            )

        self._launch()
        deadline = time.time() + timeout
        while time.time() < deadline:
            window = self._find_window()
            if window is not None:
                self._window = window
                self._window.activate()
                return
            time.sleep(0.5)
        raise RuntimeError(
            f"Launched '{self.launch_command}' but no window matching "
            f"'{self.app_title}' appeared within {timeout}s."
        )

    def _find_window(self):
        # Exact match only — app_title is expected to come from
        # list_open_windows(), not a guessed substring, so an exact match
        # is both correct and safe. Ambiguity (shouldn't happen given an
        # exact title, but checked anyway) is an error, not a guess.
        matches = [w for w in gw.getAllWindows() if w.title == self.app_title]
        if len(matches) > 1:
            raise RuntimeError(
                f"Multiple open windows have the exact title '{self.app_title}' "
                "— cannot determine which one to attach to."
            )
        return matches[0] if matches else None

    def _launch(self) -> None:
        import os

        try:
            os.startfile(self.launch_command)  # type: ignore[attr-defined]
        except OSError:
            subprocess.run(["cmd", "/c", "start", "", self.launch_command], check=True)

    def _ensure_attached(self) -> None:
        if self._window is None:
            raise RuntimeError("Not attached to a window — call attach_or_launch() first.")
        if self._window not in gw.getAllWindows():
            raise RuntimeError(f"Target window '{self.app_title}' is no longer open.")

    def _ensure_focused(self) -> None:
        self._ensure_attached()
        if gw.getActiveWindow() != self._window:
            self._window.activate()
            time.sleep(0.15)

    def click(self, x: int, y: int) -> None:
        """x, y are relative to the target window's client area — NOT
        screen coordinates. Raises if the point falls outside the window.
        """
        self._check_abort()
        self._ensure_focused()
        if not (0 <= x <= self._window.width and 0 <= y <= self._window.height):
            raise ValueError(
                f"({x}, {y}) is outside the target window's bounds "
                f"({self._window.width}x{self._window.height})."
            )
        self._check_abort()  # re-check right before acting, in case of a race
        pyautogui.moveTo(self._window.left + x, self._window.top + y, duration=0.3)
        pyautogui.click()

    def type_text(self, text: str, interval: float = 0.02, chunk_size: int = 10) -> None:
        """Focuses the target window before typing, so keystrokes can't
        land in whatever window happened to be active.

        Typed in small chunks (not one blocking call) specifically so a
        panic stop mid-sentence actually takes effect instead of only being
        checked before typing starts.
        """
        self._check_abort()
        self._ensure_focused()
        for i in range(0, len(text), chunk_size):
            self._check_abort()
            pyautogui.typewrite(text[i : i + chunk_size], interval=interval)

    def screenshot(self) -> Image.Image:
        """Captures only the target window's region, not the full desktop."""
        self._ensure_attached()
        region = (self._window.left, self._window.top, self._window.width, self._window.height)
        return pyautogui.screenshot(region=region)

    def cursor_position(self) -> tuple[int, int]:
        return pyautogui.position()
