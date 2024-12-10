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
