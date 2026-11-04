"""Tests for runconf page views."""

from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertTemplateUsed

from ...utils import LoginRequiredTest


class TestConfigView(LoginRequiredTest):
    """Test the configuration selection view."""

    endpoint = reverse("runconf:config_view")

    def test_config_view_authenticated_user(self, auth_client: Client) -> None:
        """Test that authenticated user can access config view."""
        response = auth_client.get(self.endpoint)
        assert response.status_code == HTTPStatus.OK

    def test_config_view_uses_correct_template(self, auth_client: Client) -> None:
        """Test that config view uses the correct template."""
        response = auth_client.get(self.endpoint)
        assertTemplateUsed(response, "runconf/config_view.html")

    def test_config_view_context_data(self, auth_client: Client) -> None:
        """Test that config view provides required context variables."""
        response = auth_client.get(self.endpoint)
        context = response.context
        assert "daq_versions" in context
        assert "sessions" in context
        assert "selected_config" in context
        assert len(context["daq_versions"]) > 0
        assert context["sessions"] == []
        assert context["selected_config"] is None

    def test_initial_panels(self, auth_client: Client) -> None:
        """Show empty panels and require a version before enabling sessions."""
        response = auth_client.get(self.endpoint)
        assertContains(response, "Loaded Configuration")
        assertContains(response, "Configuration Editor")
        assertContains(response, "No configuration loaded")
        assertContains(response, '<div class="card-body" id="configuration-editor"></div>')
        content = response.content.decode()
        session_select = content.split('id="daqSession"', 1)[1].split(">", 1)[0]
        assert "disabled" in session_select
        assert "required" in session_select

    @pytest.mark.parametrize("version", ["v1.0.0", "v1.1.0", "v1.2.0"])
    def test_version_selection(self, auth_client: Client, version: str) -> None:
        """Populate version-specific sessions without loading a configuration."""
        response = auth_client.get(self.endpoint, {"daq_version": version})
        assert response.context["selected_version"] == version
        assert response.context["sessions"]
        assert response.context["selected_session"] == ""
        assert response.context["selected_config"] is None
        content = response.content.decode()
        session_select = content.split('id="daqSession"', 1)[1].split(">", 1)[0]
        assert "disabled" not in session_select
        assertContains(response, "No configuration loaded")

    @pytest.mark.parametrize(
        ("selection", "error"),
        [
            ({"session": "np02-session"}, "Select a DAQ version before selecting a session."),
            ({"daq_version": "invalid"}, "Select an available DAQ version."),
            (
                {"daq_version": "v1.0.0", "session": "np02-test"},
                "Select an available session for this DAQ version.",
            ),
            (
                {"daq_version": "v1.0.0", "session": "invalid"},
                "Select an available session for this DAQ version.",
            ),
        ],
    )
    def test_invalid_selection(
        self, auth_client: Client, selection: dict[str, str], error: str
    ) -> None:
        """Reject invalid selections explicitly without showing stale metadata."""
        response = auth_client.get(self.endpoint, selection)
        assert response.context["selected_config"] is None
        assert response.context["selected_session"] == ""
        assertContains(response, error)
        assertContains(response, "No configuration loaded")

    def test_clearing_session(self, auth_client: Client) -> None:
        """Clear loaded details when the session placeholder is selected."""
        response = auth_client.get(self.endpoint, {"daq_version": "v1.0.0", "session": ""})
        assert response.context["selected_config"] is None
        assert response.context["selection_error"] == ""
        assertContains(response, "No configuration loaded")
