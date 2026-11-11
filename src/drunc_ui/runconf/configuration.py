"""Resolve and read SessionManager configurations from the local DAQ environment."""

import os
from pathlib import Path
from typing import TypedDict

from conffwk import Configuration


class LoadedConfig(TypedDict):
    """Metadata read from a selected local configuration."""

    detector_configuration: str
    daq_config: str
    current_config_file: str
    session_in_config: str
    contents: str


def load_config(file: str, session_id: str) -> LoadedConfig:
    """Resolve an unambiguous local file and read the requested Session DAL."""
    search_path = os.environ.get("DUNEDAQ_DB_PATH", "")
    if not search_path:
        raise ValueError("DUNEDAQ_DB_PATH is not set. Start drunc-ui in the DBT environment.")
    if Path(file).name != file or not file.endswith(".data.xml"):
        raise ValueError("The SessionManager configuration must be a .data.xml basename.")

    matches = {
        candidate.resolve()
        for root in search_path.split(":")
        if root
        for candidate in Path(root).rglob("*.data.xml")
        if candidate.name == file and candidate.is_file()
    }
    if not matches:
        raise FileNotFoundError(f"Configuration {file!r} was not found in DUNEDAQ_DB_PATH.")
    if len(matches) > 1:
        raise ValueError(f"Configuration {file!r} is ambiguous in DUNEDAQ_DB_PATH.")
    path = matches.pop()
    config = Configuration(f"oksconflibs:{path}")
    session = next((dal for dal in config.get_dals("Session") if dal.id == session_id), None)
    if session is None:
        raise ValueError(f"Session {session_id!r} was not found in configuration {file!r}.")
    detector = session.detector_configuration
    return {
        "detector_configuration": detector.id if detector else "Not configured",
        "daq_config": str(path),
        "current_config_file": str(path),
        "session_in_config": session.id,
        "contents": path.read_text(encoding="utf-8"),
    }
