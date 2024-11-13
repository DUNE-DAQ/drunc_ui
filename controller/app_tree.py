"""AppTree model for the application tree structure."""

from __future__ import annotations

from pydantic import BaseModel


class AppTree(BaseModel):
    """Model for the application tree structure."""

    name: str
    host: str = ""
    detector: str = ""
    children: list[AppTree] = []
