"""Unit tests for drunc_ui."""

import signal

# Windows does not have SIGHUP, so we define it here to avoid errors during tests
if not hasattr(signal, "SIGHUP"):
    signal.SIGHUP = 1  # type: ignore[attr-defined]
