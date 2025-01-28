import pytest
from django.utils.safestring import mark_safe

from controller.app_tree import AppTree


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
                    "name": mark_safe(
                        "⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ChildApp"
                    ),
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
                    "name": mark_safe(
                        "⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ChildApp1"
                    ),
                    "host": "childhost1",
                    "detector": "",
                },
                {
                    "name": mark_safe(
                        "⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ChildApp2"
                    ),
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
                            AppTree(
                                name="GrandChildApp", children=[], host="grandchildhost"
                            )
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
                    "name": mark_safe(
                        "⋅&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ChildApp"
                    ),
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
    mock_get_controller_status = mocker.patch(
        "controller.app_tree.get_controller_status"
    )
    from controller.app_tree import AppTree, get_app_tree

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
    mock_get_controller_status.assert_called_once()

    # Test with a provided status
    child_status = MockStatus("child", [])
    root_status_with_child = MockStatus("root", [child_status])
    result = get_app_tree("a_user", root_status_with_child, hostnames, detectors)
    assert result == AppTree("root", [AppTree("child", [], "unknown", "det1")], "")

    # Test with nested children
    grandchild_status = MockStatus("grandchild", [])
    child_status_with_grandchild = MockStatus("child", [grandchild_status])
    root_status_with_nested_children = MockStatus(
        "root", [child_status_with_grandchild]
    )
    result = get_app_tree(
        "a_user", root_status_with_nested_children, hostnames, detectors
    )
    assert result == AppTree(
        "root",
        [AppTree("child", [AppTree("grandchild", [], "unknown")], "unknown", "det1")],
        "",
    )
