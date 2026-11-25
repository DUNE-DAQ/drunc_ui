"""Tests for the mocked SessionManager configuration endpoints."""

from drunc_ui.runconf.configuration import create_run_config


def test_create_run_config() -> None:
    """Return a consolidated config path and a drunc command that boots it."""
    created = create_run_config("/work/np02-session.data.xml", "np02-session")
    assert created["session_id"] == "np02-session"
    assert created["source_path"] == "/work/np02-session.data.xml"
    assert created["path"].endswith(".data.xml")
    assert "/np02_" in created["path"]
    assert created["drunc_command"].startswith("drunc-unified-shell ")
    assert f" {created['path']} np02-session " in created["drunc_command"]
