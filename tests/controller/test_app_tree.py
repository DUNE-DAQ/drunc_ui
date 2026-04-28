import pytest
from django.utils.safestring import mark_safe

from drunc_ui.controller.app_tree import AppTree


@pytest.mark.parametrize(
    "app, expected",
    [
        (
            AppTree(name="App1", children=[], host="localhost"),
            [
                {
                    "name": mark_safe("App1"),
                    "host": "localhost",
                    "detector": "",
                }
            ],
        ),
        (
            AppTree(
                name="ParentApp",
                children=[AppTree(name="ChildApp", children=[], host="childhost")],
                host="parenthost",
            ),
            [
                {
                    "name": mark_safe("ParentApp"),
                    "host": "parenthost",
                    "detector": "",
                },
                {
                    "name": mark_safe("⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ChildApp"),
                    "host": "childhost",
                    "detector": "",
                },
            ],
        ),
        (
            AppTree(
                name="ParentApp",
                children=[
                    AppTree(name="ChildApp1", children=[], host="childhost1"),
                    AppTree(name="ChildApp2", children=[], host="childhost2"),
                ],
                host="parenthost",
            ),
            [
                {
                    "name": mark_safe("ParentApp"),
                    "host": "parenthost",
                    "detector": "",
                },
                {
                    "name": mark_safe("⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ChildApp1"),
                    "host": "childhost1",
                    "detector": "",
                },
                {
                    "name": mark_safe("⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ChildApp2"),
                    "host": "childhost2",
                    "detector": "",
                },
            ],
        ),
        (
            AppTree(
                name="ParentApp",
                children=[
                    AppTree(
                        name="ChildApp",
                        children=[
                            AppTree(name="GrandChildApp", children=[], host="grandchildhost")
                        ],
                        host="childhost",
                    )
                ],
                host="parenthost",
            ),
            [
                {
                    "name": mark_safe("ParentApp"),
                    "host": "parenthost",
                    "detector": "",
                },
                {
                    "name": mark_safe("⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ChildApp"),
                    "host": "childhost",
                    "detector": "",
                },
                {
                    "name": mark_safe(
                        "⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                        + "⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                        + "GrandChildApp"
                    ),
                    "host": "grandchildhost",
                    "detector": "",
                },
            ],
        ),
    ],
)
def test_apptype_to_list(app, expected):
    """Test the to_list method."""
    assert app.to_list() == expected


def test_get_app_tree(mocker):
    """Test the get_app_tree function."""
    from druncschema.controller_pb2 import StatusResponse

    from drunc_ui.controller.app_tree import AppTree, get_app_tree

    mock_get_controller_status = mocker.patch("drunc_ui.controller.app_tree.get_controller_status")

    class MockStatus:
        def __init__(self, name, children):
            self.name = name
            self.children = children

    hostnames = {"root": ""}
    detectors = {"child": "det1"}

    # Test with no status provided (default case)
    root_status = MockStatus("root", [])
    mock_get_controller_status.return_value = root_status
    result = get_app_tree("a_user", None, hostnames, detectors)
    assert result == AppTree("root", [], "")

    # Test with nested children
    status = StatusResponse(name="root")
    child_status = status.children.add()
    child_status.name = "child"
    grandchild_status = child_status.children.add()
    grandchild_status.name = "grandchild"
    result = get_app_tree("a_user", status, hostnames, detectors)
    assert result == AppTree(
        "root",
        [AppTree("child", [AppTree("grandchild", [], "unknown")], "unknown", "det1")],
        "",
    )
