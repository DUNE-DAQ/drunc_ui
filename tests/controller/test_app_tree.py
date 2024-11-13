"""Tests for the AppTree class."""

from django.utils.safestring import SafeString

from controller.app_tree import AppTree


def test_to_shoelace_tree_single_node() -> None:
    """Test that a single node is converted to a shoelace tree item."""
    tree = AppTree(name="root")
    expected_output = SafeString("<sl-tree-item expanded> root</sl-tree-item>")
    assert tree.to_shoelace_tree() == expected_output


def test_to_shoelace_tree_with_children() -> None:
    """Test that a node with children is converted to a shoelace tree item."""
    tree = AppTree(
        name="root", children=[AppTree(name="child1"), AppTree(name="child2")]
    )
    expected_output = SafeString(
        "<sl-tree-item expanded> root"
        "<sl-tree-item expanded> child1</sl-tree-item>"
        "<sl-tree-item expanded> child2</sl-tree-item>"
        "</sl-tree-item>"
    )
    assert tree.to_shoelace_tree() == expected_output


def test_to_shoelace_tree_nested_children() -> None:
    """Test that a node with nested children is converted to a shoelace tree item."""
    tree = AppTree(
        name="root",
        children=[
            AppTree(
                name="child1",
                children=[AppTree(name="grandchild1"), AppTree(name="grandchild2")],
            ),
            AppTree(name="child2"),
        ],
    )
    expected_output = SafeString(
        "<sl-tree-item expanded> root"
        "<sl-tree-item expanded> child1"
        "<sl-tree-item expanded> grandchild1</sl-tree-item>"
        "<sl-tree-item expanded> grandchild2</sl-tree-item>"
        "</sl-tree-item>"
        "<sl-tree-item expanded> child2</sl-tree-item>"
        "</sl-tree-item>"
    )
    assert tree.to_shoelace_tree() == expected_output
