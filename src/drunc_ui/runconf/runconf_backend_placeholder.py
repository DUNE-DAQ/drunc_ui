"""Mocked runconf-ui backend for the configuration editor.

``MockRunconfService`` stands in for the runconf-ui gRPC server. It has one
method per RPC of ``RunconfService`` in the runconfschema repository, as
defined on its improved_api branch:
https://github.com/DUNE-DAQ/runconfschema/tree/hwallace/feature/improved_api/schema/runconfschema

The real server is ``runconf_ui/api/grpc_service.py`` on runconf-ui's
``staging/client_server_model`` branch, and the mock follows what it does.

Requests and responses are plain dicts shaped like the protobuf messages, so
runconfschema is not a dependency yet:

- keys are the proto field names;
- enums are given by name, e.g. ``"INCLUDED"``;
- unset ``optional``/``oneof`` fields are left out;
- ``Any`` details are ``{"@type": <type URL>, **fields}``.

Once the schema is released, replace the mock with a client that converts the
real messages at this boundary.

``subscribe`` is not mocked, because the pages don't stream server state yet.
"""

from __future__ import annotations

import copy
from typing import Literal, NotRequired, TypedDict

NodeStatus = Literal["INCLUDED", "EXCLUDED", "PARENT_EXCLUDED"]
NodeGroup = Literal["TOGGLES", "ADJUSTABLE"]
RunconfCommand = Literal["QUIT", "CREATE_QUIT", "RESET", "HELP"]
NodePath = tuple[str, ...]
NodeValue = bool | int | float | str


# ---------------------------------------------------------------------------
# Messages (common.proto, configuration_access.proto, state.proto,
# main_controls.proto)
# ---------------------------------------------------------------------------


class Error(TypedDict):
    """``Error``."""

    message: str


class Response(TypedDict):
    """``Response``: the outcome of a request."""

    outcome: Literal["SUCCESS", "FAIL", "UNKNOWN"]
    message: NotRequired[str]
    error: NotRequired[Error]


class DropDownContent(TypedDict):
    """``DropDownContent``: the values listed in one dropdown."""

    values: list[str]


class Initialisation(TypedDict):
    """``Initialisation``: the dropdowns and versions a frontend starts from.

    ``structure`` maps each dropdown to its initial value, as the real server
    fills it.
    """

    daq_version: str
    apparatus: str
    structure: dict[str, str]
    dropdowns: dict[str, DropDownContent]


class DropDownSelection(TypedDict):
    """``DropDownSelection``: a value picked in a dropdown."""

    key: str
    value: str


class Open(TypedDict):
    """``Open``: open the selected configuration. The server ignores ``selection``."""

    selection: dict[str, str]


class DropDownUpdate(TypedDict):
    """``DropDownUpdate``: new dropdown contents, and the dropdowns to clear."""

    response: Response
    update: dict[str, DropDownContent]
    resets: list[str]


class ConfigTreeNode(TypedDict):
    """``ConfigTreeNode``: one entry in the configuration (DAL object) tree.

    An object is labelled ``uid@Class`` and has a state. A relationship is
    labelled with its name, has no state, and holds the objects it refers to.
    """

    label: str
    state: NotRequired[NodeStatus]
    children: list[ConfigTreeNode]


class ConfigurationInfo(TypedDict):
    """``ConfigurationInfo``: a summary of the loaded configuration."""

    response: Response
    config_open: bool
    apparatus: str
    daq_version: NotRequired[str]
    config_file: NotRequired[str]
    current_file: NotRequired[str]
    session_name: NotRequired[str]
    config_tree: list[ConfigTreeNode]


class NodeStatusInfo(TypedDict):
    """``NodeStatusInfo``: one toggle or adjustable node.

    ``node_path`` is ``[group_id, (parent,) label]``, and empty for nodes that
    can't be addressed. For toggles, ``bool_value`` is true when the node itself
    is included.
    """

    node_state: NodeStatus
    node_path: list[str]
    tooltip: NotRequired[str]
    node_group: NotRequired[NodeGroup]
    children: list[NodeStatusInfo]
    bool_value: NotRequired[bool]
    int_value: NotRequired[int]
    double_value: NotRequired[float]
    string_value: NotRequired[str]
    label: str


class GroupNodes(TypedDict):
    """``GroupNodes``: one tab of toggles or adjustable values.

    ``nodes`` is flat and in display order. ``systems`` holds the same nodes
    as a hierarchy with one root per system.
    """

    group_id: str
    node_group: NodeGroup
    nodes: list[NodeStatusInfo]
    systems: list[NodeStatusInfo]
    view_panel: NotRequired[str]


class ConfigurationOutcome(TypedDict):
    """``ConfigurationOutcome``: the result of opening a configuration."""

    response: Response
    groups: list[GroupNodes]


class ResponseNodeGroups(TypedDict):
    """``ResponseNodeGroups``: every group, toggles first."""

    response: Response
    groups: list[GroupNodes]


class RequestNodeStatus(TypedDict):
    """``RequestNodeStatus``: ask for one node."""

    node_group: NodeGroup
    path: list[str]


class RequestSetNodeValue(TypedDict):
    """``RequestSetNodeValue``: set one node, with exactly one value field."""

    node_group: NodeGroup
    path: list[str]
    double_value: NotRequired[float]
    bool_value: NotRequired[bool]
    node_status_value: NotRequired[NodeStatus]
    int_value: NotRequired[int]
    string_value: NotRequired[str]


class ResponseNodeStatus(TypedDict):
    """``ResponseNodeStatus``: the nodes that changed, or the one requested."""

    response: Response
    nodes: list[NodeStatusInfo]


class RunconfCommandRequest(TypedDict):
    """``RunconfCommandRequest``."""

    command: RunconfCommand


CommandDetails = TypedDict(
    "CommandDetails",
    {"@type": str, "value": NotRequired[str], "groups": NotRequired[list[GroupNodes]]},
)
"""A message packed in an ``Any``: a ``StringValue`` with ``value``, or a
``ConfigurationOutcome`` with ``groups`` and its ``response`` left unset.
"""


class RunconfCommandResponse(TypedDict):
    """``RunconfCommandResponse``.

    ``details`` is packed in an ``Any``:

    - ``CREATE_QUIT``: a ``StringValue`` holding the created configuration's path;
    - ``RESET``: a ``ConfigurationOutcome`` holding the reset groups;
    - ``HELP``: a ``StringValue`` holding the help text;
    - ``QUIT``: no details.
    """

    response: Response
    command: RunconfCommand
    details: NotRequired[CommandDetails]


STRING_VALUE_TYPE = "type.googleapis.com/google.protobuf.StringValue"
CONFIGURATION_OUTCOME_TYPE = "type.googleapis.com/dunedaq.runconfschema.ConfigurationOutcome"


class RunconfServiceError(Exception):
    """A request the server rejects with a gRPC status, not a FAIL ``Response``."""

    def __init__(self, code: str, details: str) -> None:
        """Store the gRPC status code name, e.g. ``FAILED_PRECONDITION``."""
        super().__init__(f"{code}: {details}")
        self.code = code
        self.details = details


# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------


class MockCatalogue(TypedDict):
    """What the mocked server lists: an apparatus, its versions and their sessions."""

    apparatus: str
    default_version: str
    sessions: dict[str, list[str]]


MOCK_CATALOGUE: MockCatalogue = {
    "apparatus": "np02",
    "default_version": "fddaq-v5.3.0",
    "sessions": {
        "fddaq-v5.3.0": [
            "hd-coldbox-session",
            "np02-emu-session",
            "np02-session",
            "np02-tde-session",
            "np04-emu-session",
            "np04-session",
        ]
    },
}

_MOCK_PROD_ROOT = "/mock/prod-configs"
_MOCK_WORKING_ROOT = "/mock/working-copies"
_MOCK_RUN_CONFIG_ROOT = "/mock/run-configs"

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


def _session_apparatus(session_name: str) -> str:
    return session_name.removesuffix("-session")


def mock_config_xml(session_name: str) -> str:
    """Return the OKS XML of the mocked production configuration for a session."""
    return _MOCK_XML.format(session_id=session_name, apparatus=_session_apparatus(session_name))


def _mock_config_tree(session_name: str) -> list[ConfigTreeNode]:
    """Return the entries below the Session of ``mock_config_xml``, in XML order.

    Every object is included, because the Session has no ``excluded`` relation.
    The real tree nests each drawn relationship under the previous one; this
    keeps them side by side, which is what the schema describes.
    """
    apparatus = _session_apparatus(session_name)
    relations = [
        ("environment", "VariableSet", f"{apparatus}-common-env"),
        ("segment", "Segment", f"{apparatus}-root-segment"),
        ("infrastructure_applications", "ConnectivityService", "local-connection-server"),
        ("detector_configuration", "DetectorConfig", f"{apparatus}-detector-config"),
        ("opmon_uri", "OpMonURI", f"{apparatus}-opmon-uri"),
    ]
    return [
        {
            "label": relation,
            "children": [{"label": f"{uid}@{cls}", "state": "INCLUDED", "children": []}],
        }
        for relation, cls, uid in relations
    ]


class _MockNode(TypedDict):
    label: str
    tooltip: str
    value: NodeValue | None
    """``None`` for a system root, which has no value of its own."""
    children: list[_MockNode]


class _MockGroup(TypedDict):
    group_id: str
    node_group: NodeGroup
    view_panel: NotRequired[str]
    systems: list[_MockNode]
    """Each system's root is drawn but can't be addressed. Its descendants can."""


def _toggle(label: str, tooltip: str, *children: _MockNode) -> _MockNode:
    return {"label": label, "tooltip": tooltip, "value": True, "children": list(children)}


def _system(label: str, tooltip: str, *children: _MockNode) -> _MockNode:
    return {"label": label, "tooltip": tooltip, "value": None, "children": list(children)}


_MOCK_GROUPS: list[_MockGroup] = [
    {
        "group_id": "readout",
        "node_group": "TOGGLES",
        "view_panel": "Readout Map",
        "systems": [
            _system(
                "Readout",
                "Detector readout",
                _toggle(
                    "crp4",
                    "Charge readout plane 4",
                    _toggle("wib-0", "WIB 0 of CRP 4"),
                    _toggle("wib-1", "WIB 1 of CRP 4"),
                ),
                _toggle(
                    "crp5",
                    "Charge readout plane 5",
                    _toggle("wib-0", "WIB 0 of CRP 5"),
                    _toggle("wib-1", "WIB 1 of CRP 5"),
                ),
            )
        ],
    },
    {
        "group_id": "trigger",
        "node_group": "ADJUSTABLE",
        "systems": [
            _system(
                "Trigger",
                "Trigger settings",
                {
                    "label": "random_trigger_rate_hz",
                    "tooltip": "Rate of random triggers, in Hz",
                    "value": 1.0,
                    "children": [],
                },
                {
                    "label": "ttcm_prescale",
                    "tooltip": "Prescale applied to timing triggers",
                    "value": 1,
                    "children": [],
                },
            )
        ],
    },
]


_VALUE_FIELDS: dict[type, str] = {
    bool: "bool_value",
    int: "int_value",
    float: "double_value",
    str: "string_value",
}
_REQUEST_VALUE_FIELDS = (
    "double_value",
    "bool_value",
    "node_status_value",
    "int_value",
    "string_value",
)

HELP_TEXT = """runconf-ui gRPC service (mocked)
  1. initialise         - current dropdown contents and versions
  2. select_dropdown    - pick 'version', then 'session'
  3. open_configuration - load the selected session, returns the node groups
  4. get/set_node_state - inspect or change toggles and adjustable values
  5. get_node_groups / get_configuration_info - full state for drawing
  runconf_command: QUIT (no save), CREATE_QUIT (save then quit), RESET, HELP
"""


def _ok(message: str) -> Response:
    return {"outcome": "SUCCESS", "message": message}


def _fail(message: str, error: str) -> Response:
    return {"outcome": "FAIL", "message": message, "error": {"message": error}}


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class MockRunconfService:
    """An in-memory, already-booted stand-in for the runconf-ui gRPC server.

    Like the real server, it holds the selected version and session, the open
    configuration, and the edits made to it. It stops answering after
    ``QUIT`` or ``CREATE_QUIT``.
    """

    def __init__(self, catalogue: MockCatalogue = MOCK_CATALOGUE) -> None:
        """Serve ``catalogue``, with nothing selected yet."""
        self._catalogue = copy.deepcopy(catalogue)
        self._version: str | None = None
        self._session: str | None = None
        self._open_session: str | None = None
        self._values: dict[NodePath, NodeValue] = {}
        self._stopped = False

    # ---- helpers ----

    def _check_running(self) -> None:
        if self._stopped:
            raise RunconfServiceError("UNAVAILABLE", "Server has shut down")

    def _check_open(self) -> str:
        self._check_running()
        if self._open_session is None:
            raise RunconfServiceError(
                "FAILED_PRECONDITION", "No configuration open; call open_configuration first"
            )
        return self._open_session

    def _dropdowns(self) -> dict[str, DropDownContent]:
        sessions = self._catalogue["sessions"].get(self._version or "", [])
        return {
            "version": {"values": list(self._catalogue["sessions"])},
            "session": {"values": list(sessions)},
        }

    def _addressable(self) -> dict[NodePath, tuple[_MockGroup, _MockNode, NodePath | None]]:
        """Return every addressable node, by path, with its group and its parent's path."""
        out: dict[NodePath, tuple[_MockGroup, _MockNode, NodePath | None]] = {}

        def walk(group: _MockGroup, node: _MockNode, parent: NodePath | None) -> None:
            path = (*(parent or (group["group_id"],)), node["label"])
            out[path] = (group, node, parent)
            for child in node["children"]:
                walk(group, child, path)

        for group in _MOCK_GROUPS:
            for system in group["systems"]:
                for node in system["children"]:
                    walk(group, node, None)
        return out

    def _value(self, path: NodePath | None, node: _MockNode) -> NodeValue | None:
        return node["value"] if path is None else self._values.get(path, node["value"])

    def _state(self, path: NodePath | None, node: _MockNode) -> NodeStatus:
        """Return a node's state, taking every ancestor into account."""
        if path is None:
            return "INCLUDED"
        nodes = self._addressable()
        parent = nodes[path][2]
        while parent is not None:
            if self._value(parent, nodes[parent][1]) is False:
                return "PARENT_EXCLUDED"
            parent = nodes[parent][2]
        return "EXCLUDED" if self._value(path, node) is False else "INCLUDED"

    def _info(
        self, group: _MockGroup, node: _MockNode, path: NodePath | None, *, nested: bool
    ) -> NodeStatusInfo:
        info: NodeStatusInfo = {
            "node_state": self._state(path, node),
            "node_path": list(path or ()),
            "tooltip": node["tooltip"],
            "node_group": group["node_group"],
            "children": [],
            "label": node["label"],
        }
        value = self._value(path, node)
        if value is not None:
            info[_VALUE_FIELDS[type(value)]] = value  # type: ignore[literal-required]
        if nested:
            base = path or (group["group_id"],)
            info["children"] = [
                self._info(group, child, (*base, child["label"]), nested=True)
                for child in node["children"]
            ]
        return info

    def _groups(self) -> list[GroupNodes]:
        nodes = self._addressable()
        out: list[GroupNodes] = []
        for group in _MOCK_GROUPS:
            message: GroupNodes = {
                "group_id": group["group_id"],
                "node_group": group["node_group"],
                "nodes": [
                    self._info(g, node, path, nested=False)
                    for path, (g, node, _) in nodes.items()
                    if g is group
                ],
                "systems": [
                    self._info(group, system, None, nested=True) for system in group["systems"]
                ],
            }
            if "view_panel" in group:
                message["view_panel"] = group["view_panel"]
            out.append(message)
        return out

    def _snapshot(self) -> dict[NodePath, NodeStatusInfo]:
        return {
            path: self._info(group, node, path, nested=False)
            for path, (group, node, _) in self._addressable().items()
        }

    # ---- RPCs ----

    def initialise(self) -> Initialisation:
        """``initialise``: the dropdowns and versions as they currently are."""
        self._check_running()
        return {
            "daq_version": self._version or "",
            "apparatus": self._catalogue["apparatus"],
            "structure": {"version": self._catalogue["default_version"]},
            "dropdowns": self._dropdowns(),
        }

    def select_dropdown(self, request: DropDownSelection) -> DropDownUpdate:
        """``select_dropdown``: pick a ``version`` or a ``session``, or clear it with ``""``."""
        self._check_running()
        key, value = request["key"].lower(), request["value"]
        resets: list[str] = []
        if key == "version":
            if value and value not in self._catalogue["sessions"]:
                response = _fail(f"Failed to set {key}", f"{value!r} is not an available version")
            else:
                self._version = value or None
                self._session = None
                resets = ["session"]
                response = _ok(f"Set {key} to {value}")
        elif key == "session":
            if value and value not in self._dropdowns()["session"]["values"]:
                response = _fail(f"Failed to set {key}", f"{value!r} is not an available session")
            else:
                self._session = value or None
                response = _ok(f"Set {key} to {value}")
        else:
            response = _fail(f"Failed to set {key}", f"Unknown dropdown {request['key']!r}")
        return {"response": response, "update": self._dropdowns(), "resets": resets}

    def open_configuration(self, request: Open) -> ConfigurationOutcome:
        """``open_configuration``: load the selected session, discarding any edits.

        Like the real server, this ignores ``request["selection"]`` and opens
        what ``select_dropdown`` selected.
        """
        self._check_running()
        if self._session is None:
            return {
                "response": _fail("Failed to open configuration", "No session selected"),
                "groups": [],
            }
        self._open_session = self._session
        self._values = {}
        return {"response": _ok("Opened configuration"), "groups": self._groups()}

    def get_configuration_info(self) -> ConfigurationInfo:
        """``get_configuration_info``: the open configuration's files and tree."""
        self._check_running()
        info: ConfigurationInfo = {
            "response": _ok("Configuration info"),
            "config_open": self._open_session is not None,
            "apparatus": self._catalogue["apparatus"],
            "config_tree": [],
        }
        if self._open_session is not None:
            session = self._open_session
            info["daq_version"] = self._version or ""
            info["config_file"] = f"{_MOCK_PROD_ROOT}/{session}.data.xml"
            info["current_file"] = f"{_MOCK_WORKING_ROOT}/{session}.data.xml"
            info["session_name"] = session
            info["config_tree"] = _mock_config_tree(session)
        return info

    def get_node_groups(self) -> ResponseNodeGroups:
        """``get_node_groups``: every group of the open configuration."""
        self._check_open()
        return {"response": _ok("Node groups"), "groups": self._groups()}

    def get_node_state(self, request: RequestNodeStatus) -> ResponseNodeStatus:
        """``get_node_state``: one node of the open configuration."""
        self._check_open()
        path = tuple(request["path"])
        snapshot = self._snapshot()
        if path not in snapshot:
            return {
                "response": _fail(f"Node {list(path)} not found", f"No node at {list(path)}"),
                "nodes": [],
            }
        return {"response": _ok(f"Found {path[-1]}"), "nodes": [snapshot[path]]}

    def set_node_state(self, request: RequestSetNodeValue) -> ResponseNodeStatus:
        """``set_node_state``: change one node, returning every node that changed."""
        self._check_open()
        path = tuple(request["path"])
        fields = [field for field in _REQUEST_VALUE_FIELDS if field in request]
        nodes = self._addressable()
        error = ""
        if path not in nodes:
            error = f"No node at {list(path)}"
        elif len(fields) != 1:
            error = "Set exactly one node_value field"
        elif nodes[path][0]["node_group"] != request["node_group"]:
            error = f"{list(path)} is not in {request['node_group']}"
        if error:
            return {"response": _fail(f"Failed to set {list(path)}", error), "nodes": []}

        current = nodes[path][1]["value"]
        assert current is not None, "Only system roots have no value, and they can't be set"
        raw = request[fields[0]]  # type: ignore[literal-required]
        try:
            if fields[0] == "node_status_value":
                if raw == "PARENT_EXCLUDED":
                    raise ValueError("PARENT_EXCLUDED is derived and cannot be set")
                raw = raw == "INCLUDED"
            if isinstance(current, bool) != isinstance(raw, bool):
                raise ValueError("Toggles take a bool or a status, adjustables a value")
            value = raw if type(raw) is type(current) else type(current)(raw)
        except (TypeError, ValueError) as e:
            return {"response": _fail(f"Failed to set {list(path)}", str(e)), "nodes": []}

        before = self._snapshot()
        self._values[path] = value
        changed = [info for key, info in self._snapshot().items() if before[key] != info]
        return {"response": _ok(f"Set {path[-1]} to {value}"), "nodes": changed}

    def reset_node_state(self) -> ResponseNodeStatus:
        """``reset_node_state``: discard every edit, returning every node."""
        self._check_open()
        self._values = {}
        return {"response": _ok("Reset"), "nodes": list(self._snapshot().values())}

    def runconf_command(self, request: RunconfCommandRequest) -> RunconfCommandResponse:
        """``runconf_command``: quit, create and quit, reset, or show help."""
        self._check_running()
        command = request["command"]
        if command == "QUIT":
            self._stopped = True
            return {"response": _ok("Shutting down without saving"), "command": command}
        if command == "HELP":
            return {
                "response": _ok("Help"),
                "command": command,
                "details": {"@type": STRING_VALUE_TYPE, "value": HELP_TEXT},
            }
        session = self._open_session
        if session is None:
            return {
                "response": _fail(f"{command} failed", "No configuration open"),
                "command": command,
            }
        if command == "CREATE_QUIT":
            self._stopped = True
            path = f"{_MOCK_RUN_CONFIG_ROOT}/{_session_apparatus(session)}_20260101T000000.data.xml"
            return {
                "response": _ok("Configuration saved; shutting down"),
                "command": command,
                "details": {"@type": STRING_VALUE_TYPE, "value": path},
            }
        outcome = self.open_configuration({"selection": {}})
        return {
            "response": _ok("Reset"),
            "command": command,
            "details": {"@type": CONFIGURATION_OUTCOME_TYPE, "groups": outcome["groups"]},
        }


def get_runconf_service() -> MockRunconfService:
    """Return the runconf-ui server for this request.

    The pages are stateless, so they get a fresh mock each time and replay the
    selection from the request. A real client would connect to a running server.
    """
    return MockRunconfService()
