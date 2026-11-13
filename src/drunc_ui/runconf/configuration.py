"""Production configuration catalogue for the configuration editor.

``list_production_configs`` returns a mocked response from a proposed SessionManager
endpoint of the same name. Once the endpoint exists in druncschema and drunc, this
function should be replaced by a call through ``session_manager_interface``.
"""

import copy
from typing import TypedDict


class ProductionConfig(TypedDict):
    """One Session in a production configuration file (``ConfigKey`` plus its path)."""

    file: str
    session_id: str
    path: str


class ProductionConfigs(TypedDict):
    """Response of the proposed ``list_production_configs`` endpoint."""

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


class ProductionConfigCopy(TypedDict):
    """Response of the proposed ``get_production_config`` endpoint."""

    file: str
    session_id: str
    path: str
    working_path: str
    contents: str


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


def list_production_configs() -> ProductionConfigs:
    """Return a mocked response from the proposed ``list_production_configs`` endpoint.

    The sessions match those the SessionManager lists once the production
    configuration setup script has been sourced.
    """
    return copy.deepcopy(_MOCK_RESPONSE)


def get_production_config(file: str, session_id: str) -> ProductionConfigCopy:
    """Return a mocked response from the proposed ``get_production_config`` endpoint.

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
    }
