"""Tests for local configuration resolution and reading."""

from types import SimpleNamespace

import pytest

from drunc_ui.runconf.configuration import load_config


@pytest.fixture
def local_config(tmp_path, monkeypatch, mocker):
    """Provide local files and mock only the OKS parser."""
    path = tmp_path / "nested" / "example.data.xml"
    path.parent.mkdir()
    path.write_text('<oks-data description="detector café"/>\n', encoding="utf-8")
    monkeypatch.setenv("DUNEDAQ_DB_PATH", str(tmp_path))
    parser = mocker.patch("drunc_ui.runconf.configuration.Configuration")
    parser.return_value.get_dals.return_value = [
        SimpleNamespace(id="other", detector_configuration=None),
        SimpleNamespace(id="selected", detector_configuration=SimpleNamespace(id="detector")),
    ]
    return path, parser


def test_load_config(local_config):
    """Read the selected Session, not simply the first DAL."""
    path, parser = local_config
    result = load_config(path.name, "selected")
    parser.assert_called_once_with(f"oksconflibs:{path}")
    assert result == {
        "detector_configuration": "detector",
        "daq_config": str(path),
        "current_config_file": str(path),
        "session_in_config": "selected",
        "contents": '<oks-data description="detector café"/>\n',
    }


def test_overlapping_paths(local_config, monkeypatch):
    """Do not treat the same file discovered under overlapping roots as ambiguous."""
    path, _ = local_config
    monkeypatch.setenv("DUNEDAQ_DB_PATH", f"{path.parent}:{path.parent.parent}:")
    assert load_config(path.name, "selected")["daq_config"] == str(path)


def test_ambiguous_file(local_config):
    """Reject duplicate basenames rather than loading an arbitrary configuration."""
    path, parser = local_config
    (path.parent.parent / path.name).touch()
    with pytest.raises(ValueError, match="ambiguous"):
        load_config(path.name, "selected")
    parser.assert_not_called()


def test_missing_file(local_config):
    """Reject a catalogue entry which cannot be resolved locally."""
    with pytest.raises(FileNotFoundError, match="not found"):
        load_config("missing.data.xml", "selected")


def test_missing_session(local_config):
    """Reject stale SessionManager IDs."""
    with pytest.raises(ValueError, match=r"Session .* was not found"):
        load_config(local_config[0].name, "missing")


def test_missing_search_path(monkeypatch):
    """Require the DAQ database search path."""
    monkeypatch.delenv("DUNEDAQ_DB_PATH", raising=False)
    with pytest.raises(ValueError, match="DUNEDAQ_DB_PATH is not set"):
        load_config("example.data.xml", "selected")


@pytest.mark.parametrize("file", ["../example.data.xml", "/tmp/example.data.xml", "other.txt"])
def test_invalid_basename(local_config, file):
    """Only resolve basenames advertised by the service."""
    with pytest.raises(ValueError, match="basename"):
        load_config(file, "selected")


def test_parse_error(local_config):
    """Preserve parser failures for the view to report."""
    path, parser = local_config
    parser.side_effect = RuntimeError("invalid OKS")
    with pytest.raises(RuntimeError, match="invalid OKS"):
        load_config(path.name, "selected")


def test_read_error(local_config, mocker):
    """Propagate file read errors instead of showing an empty editor."""
    path, _ = local_config
    mocker.patch("pathlib.Path.read_text", side_effect=PermissionError("read denied"))
    with pytest.raises(PermissionError, match="read denied"):
        load_config(path.name, "selected")
