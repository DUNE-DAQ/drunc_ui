"""Production configuration catalogue for the configuration editor.

The functions here return mocked SessionManager responses. Once the matching
endpoints exist in druncschema and drunc, replace them with calls through
``session_manager_interface``.
"""

import copy
from typing import TypedDict


class ProductionConfig(TypedDict):
    """One Session in a production configuration file (``ConfigKey`` plus its path)."""

    file: str
    session_id: str
    path: str


class ProductionConfigs(TypedDict):
    """Response of the ``list_production_configs`` endpoint."""

    daq_version: str
    apparatus: str
    configs: list[ProductionConfig]


_MOCK_ROOT = "/mock/prod-configs"
_MOCK_SESSIONS = [
    "hd-coldbox-session",
    "np02-emu-session",
    "np02-session",
    "np02-tde-session",
    "np04-emu-session",
    "np04-session",
]
_MOCK_RESPONSE: ProductionConfigs = {
    "daq_version": "fddaq-v5.3.0",
    "apparatus": "np02",
    "configs": [
        {
            "file": f"{session}.data.xml",
            "session_id": session,
            "path": f"{_MOCK_ROOT}/{session}.data.xml",
        }
        for session in _MOCK_SESSIONS
    ],
}


ConfigNode = TypedDict(
    "ConfigNode",
    {
        "id": str,
        "class": str,
        "state": str,
        "relations": dict[str, list["ConfigNode"]],
    },
)
"""One object in the configuration tree, with the objects it relates to by relation name.

``state`` is ``INCLUDED``, ``EXCLUDED`` or ``PARENT_EXCLUDED``, as computed by runconf-ui.
"""


class ProductionConfigWorkingCopy(TypedDict):
    """Response of the ``get_production_config`` endpoint."""

    file: str
    session_id: str
    path: str
    working_path: str
    contents: str
    tree: ConfigNode


_MOCK_WORKING_ROOT = "/mock/working-copies"
_MOCK_XML = """<?xml version="1.0" encoding="ASCII"?>

<!-- oks-data version 2.2 -->

<oks-data>

<info name="" type="" num-of-items="2" oks-format="data" oks-version="oks-08-03-04"/>

<include>
 <file path="confmodel/dunedaq-common.schema.xml"/>
 <file path="appmodel/application.schema.xml"/>
 <file path="{apparatus}-segments.data.xml"/>
 <file path="{apparatus}-detector.data.xml"/>
</include>

<obj class="Session" id="{session_id}">
 <attr name="data_request_timeout_ms" type="u32" val="1000"/>
 <attr name="data_rate_slowdown_factor" type="u32" val="1"/>
 <attr name="rte_script" type="string" val=""/>
 <rel name="environment">
  <ref class="VariableSet" id="{apparatus}-common-env"/>
 </rel>
 <rel name="segment" class="Segment" id="{apparatus}-root-segment"/>
 <rel name="infrastructure_applications">
  <ref class="ConnectivityService" id="local-connection-server"/>
 </rel>
 <rel name="detector_configuration" class="DetectorConfig" id="{apparatus}-detector-config"/>
 <rel name="opmon_uri" class="OpMonURI" id="{apparatus}-opmon-uri"/>
</obj>

<obj class="DetectorConfig" id="{apparatus}-detector-config">
 <attr name="op_env" type="string" val="{apparatus}"/>
 <attr name="offline_data_stream" type="string" val="cosmics"/>
 <attr name="clock_speed_hz" type="u32" val="62500000"/>
</obj>

</oks-data>
"""


def _mock_node(class_name: str, object_id: str) -> ConfigNode:
    """Return an included tree node with no related objects."""
    return {"id": object_id, "class": class_name, "state": "INCLUDED", "relations": {}}


def _mock_tree(session_id: str, apparatus: str) -> ConfigNode:
    """Return the configuration tree of ``_MOCK_XML``, rooted at its Session.

    Relations are listed in the order they appear in the XML. Nothing is
    excluded, because the Session has no ``excluded`` relation.
    """
    return {
        "id": session_id,
        "class": "Session",
        "state": "INCLUDED",
        "relations": {
            "environment": [_mock_node("VariableSet", f"{apparatus}-common-env")],
            "segment": [_mock_node("Segment", f"{apparatus}-root-segment")],
            "infrastructure_applications": [
                _mock_node("ConnectivityService", "local-connection-server")
            ],
            "detector_configuration": [
                _mock_node("DetectorConfig", f"{apparatus}-detector-config")
            ],
            "opmon_uri": [_mock_node("OpMonURI", f"{apparatus}-opmon-uri")],
        },
    }


def list_production_configs() -> ProductionConfigs:
    """Return a mocked ``list_production_configs`` response.

    The sessions match those the SessionManager lists once the production
    configuration setup script has been sourced.
    """
    return copy.deepcopy(_MOCK_RESPONSE)


def get_production_config(file: str, session_id: str) -> ProductionConfigWorkingCopy:
    """Return a mocked ``get_production_config`` response.

    The SessionManager would copy the production configuration to a working
    location and return the copy, which later editing features would modify.
    """
    config = next(
        (
            config
            for config in _MOCK_RESPONSE["configs"]
            if (config["file"], config["session_id"]) == (file, session_id)
        ),
        None,
    )
    if config is None:
        raise ValueError(f"Session {session_id!r} in {file!r} is not a production configuration.")
    apparatus = session_id.removesuffix("-session")
    return {
        **config,
        "working_path": f"{_MOCK_WORKING_ROOT}/{file}",
        "contents": _MOCK_XML.format(session_id=session_id, apparatus=apparatus),
        "tree": _mock_tree(session_id, apparatus),
    }


class CreatedRunConfig(TypedDict):
    """Response of the ``create_run_config`` endpoint."""

    session_id: str
    source_path: str
    path: str
    drunc_command: str


_MOCK_RUN_CONFIG_ROOT = "/mock/run-configs"
_MOCK_PROCESS_MANAGER = "ssh-standalone"
_MOCK_SESSION_NAME = "mock-session"


def create_run_config(working_path: str, session_id: str) -> CreatedRunConfig:
    """Return a mocked ``create_run_config`` response.

    The SessionManager would do what runconf-ui's ``save_config`` does: commit
    the working copy, write a consolidated ``<apparatus>_<time>.data.xml`` and
    return its path along with the drunc command that boots it.
    """
    apparatus = session_id.removesuffix("-session")
    path = f"{_MOCK_RUN_CONFIG_ROOT}/{apparatus}_20260101T000000.data.xml"
    return {
        "session_id": session_id,
        "source_path": working_path,
        "path": path,
        "drunc_command": (
            f"drunc-unified-shell {_MOCK_PROCESS_MANAGER} {path} {session_id} {_MOCK_SESSION_NAME}"
        ),
    }
