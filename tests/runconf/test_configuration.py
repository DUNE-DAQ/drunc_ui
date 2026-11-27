"""Tests for the mocked SessionManager configuration endpoints."""

import xml.etree.ElementTree as ET

import pytest

from drunc_ui.runconf.configuration import (
    create_run_config,
    get_production_config,
    list_production_configs,
)


def test_create_run_config() -> None:
    """Return a consolidated config path and a drunc command that boots it."""
    created = create_run_config("/work/np02-session.data.xml", "np02-session")
    assert created["session_id"] == "np02-session"
    assert created["source_path"] == "/work/np02-session.data.xml"
    assert created["path"].endswith(".data.xml")
    assert "/np02_" in created["path"]
    assert created["drunc_command"].startswith("drunc-unified-shell ")
    assert f" {created['path']} np02-session " in created["drunc_command"]


def _xml_relations(contents: str, class_name: str, object_id: str) -> dict[str, list[tuple]]:
    """Return ``{relation: [(class, id), ...]}`` for one object in OKS XML."""
    root = ET.fromstring(contents)
    obj = next(
        o for o in root.iter("obj") if (o.get("class"), o.get("id")) == (class_name, object_id)
    )
    relations: dict[str, list[tuple]] = {}
    for rel in obj.iter("rel"):
        refs = [(r.get("class"), r.get("id")) for r in rel.iter("ref")]
        relations[rel.get("name")] = refs or [(rel.get("class"), rel.get("id"))]
    return relations


@pytest.mark.parametrize(
    "config", list_production_configs()["configs"], ids=lambda config: config["session_id"]
)
def test_tree_matches_xml(config) -> None:
    """The mock tree's Session relations are exactly those in the mock XML, in order."""
    copy = get_production_config(config["file"], config["session_id"])
    tree = copy["tree"]
    assert (tree["class"], tree["id"]) == ("Session", config["session_id"])
    expected = _xml_relations(copy["contents"], "Session", config["session_id"])
    actual = {
        name: [(node["class"], node["id"]) for node in nodes]
        for name, nodes in tree["relations"].items()
    }
    assert list(actual.items()) == list(expected.items())
    for nodes in tree["relations"].values():
        for node in nodes:
            assert node["state"] == "INCLUDED"
            assert node["relations"] == {}
