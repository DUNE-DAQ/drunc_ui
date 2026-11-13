"""Tests for the mocked production configuration catalogue."""

from xml.etree import ElementTree

import pytest

from drunc_ui.runconf.configuration import get_production_config, list_production_configs


def test_mock_response_shape():
    """Return the fields the proposed endpoint provides, one entry per session."""
    listing = list_production_configs()
    assert listing["daq_version"]
    assert listing["apparatus"] == "np02"
    sessions = {config["session_id"] for config in listing["configs"]}
    assert {"np02-session", "np04-session", "hd-coldbox-session"} <= sessions
    for config in listing["configs"]:
        assert config["file"] == f"{config['session_id']}.data.xml"
        assert config["path"].endswith(f"/{config['file']}")


def test_mock_response_is_a_copy():
    """Callers cannot change the mock response seen by later requests."""
    list_production_configs()["configs"].clear()
    assert list_production_configs()["configs"]


def test_get_production_config():
    """Return a working copy of a listed configuration."""
    config = list_production_configs()["configs"][0]
    copy = get_production_config(config["file"], config["session_id"])
    assert copy["path"] == config["path"]
    assert copy["working_path"] != copy["path"]
    assert copy["working_path"].endswith(f"/{config['file']}")
    ElementTree.fromstring(copy["contents"])
    assert f'<obj class="Session" id="{config["session_id"]}">' in copy["contents"]


def test_get_unknown_config():
    """Reject configurations that were not listed."""
    with pytest.raises(ValueError, match="not a production configuration"):
        get_production_config("appSession.data.xml", "test-session")
