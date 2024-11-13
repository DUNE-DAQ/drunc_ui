"""AppTree model for the application tree structure."""

from __future__ import annotations

from django.utils.safestring import SafeString, mark_safe
from pydantic import BaseModel


class AppTree(BaseModel):
    """Model for the application tree structure."""

    name: str
    host: str = ""
    detector: str = ""
    children: list[AppTree] = []

    @classmethod
    def from_drunc(cls) -> AppTree:
        """Returns the application tree structure from the controller.

        TODO: This method is a placeholder for the actual implementation.
        """
        return cls._dummy_tree()

    def to_shoelace_tree(self) -> SafeString:
        """Returns the application tree structure as a Shoelace tree."""
        return mark_safe(
            f"<sl-tree-item expanded> {self.name}"
            + "".join(child.to_shoelace_tree() for child in self.children)
            + "</sl-tree-item>"
        )

    @classmethod
    def _dummy_tree(cls) -> AppTree:
        """Returns a dummy application tree structure.

        TODO: Delete this method or make it a fixture for tests once the controller is
          implemented.
        """
        return AppTree(
            name="root",
            children=[
                AppTree(
                    name="segment_1",
                    host="localhost:8000",
                    children=[
                        AppTree(
                            name="app_1",
                            host="localhost:8002",
                            detector="neutrinos",
                        ),
                        AppTree(
                            name="app_2",
                            host="localhost:8003",
                            detector="positrons",
                        ),
                    ],
                ),
                AppTree(
                    name="segment_2",
                    host="localhost:8001",
                    children=[
                        AppTree(
                            name="app_3",
                            host="localhost:8004",
                            detector="hadrons",
                            children=[
                                AppTree(
                                    name="app_3.1",
                                    host="localhost:8006",
                                    detector="neutrons",
                                ),
                                AppTree(
                                    name="app_3.2",
                                    host="localhost:8007",
                                    detector="protons",
                                ),
                            ],
                        ),
                        AppTree(
                            name="app_4",
                            host="localhost:8005",
                            detector="photons",
                        ),
                    ],
                ),
            ],
        )
