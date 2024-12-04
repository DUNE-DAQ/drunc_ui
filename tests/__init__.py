"""Unit tests for drunc_ui."""

import platform
import signal

# Windows does not have SIGHUP, so we define it here to avoid errors during tests
if platform.system() == "Windows":
    signal.SIGHUP = 1  # type: ignore[attr-defined]
