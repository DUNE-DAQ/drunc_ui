"""Tests for runconf page views."""

import json
from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from ...utils import LoginRequiredTest


@pytest.fixture(autouse=True)
def config_catalogue(monkeypatch, mocker):
    """Provide a real-shaped catalogue without contacting a running service."""
    monkeypatch.setenv("SPACK_RELEASE", "v1.0.0")
    return mocker.patch(
        "drunc_ui.interfaces.session_manager_interface.get_configs",
        return_value=[
            {"file": "first.data.xml", "session_id": "shared"},
            {"file": "second.data.xml", "session_id": "shared"},
            {"file": "first.data.xml", "session_id": "another"},
        ],
    )


class TestConfigView(LoginRequiredTest):
    """Test the configuration selection view."""

    endpoint = reverse("runconf:config_view")

    def test_config_view_authenticated_user(self, auth_client: Client) -> None:
        """Test that authenticated user can access config view."""
        response = auth_client.get(self.endpoint)
        assert response.status_code == HTTPStatus.OK

    def test_config_view_unauthenticated_user(self, client: Client) -> None:
        """Test that an unauthenticated user is redirected to the login page."""
        response = client.get(self.endpoint)
        assertRedirects(response, reverse("main:login") + f"?next={self.endpoint}")

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
        assertContains(response, "Select a configuration to view its XML.")
        assert 'id="configuration-contents"' not in response.content.decode()
        content = response.content.decode()
        session_select = content.split('id="daqSession"', 1)[1].split(">", 1)[0]
        assert "disabled" in session_select
        assert "required" in session_select

    @pytest.mark.parametrize("version", ["v1.0.0"])
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
        assertContains(response, "shared (first.data.xml)")
        assertContains(response, "shared (second.data.xml)")
        assert len({session["value"] for session in response.context["sessions"]}) == 3

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

    def test_load_selection(self, auth_client, mocker):
        """Use both file and session identity, and render metadata read from disk."""
        loader = mocker.patch(
            "drunc_ui.runconf.views.pages.load_config",
            return_value={
                "detector_configuration": "actual-detector",
                "daq_config": "/configs/second.data.xml",
                "current_config_file": "/configs/second.data.xml",
                "session_in_config": "shared",
                "contents": '<oks-data>café</oks-data></textarea><script>alert("x")</script>',
            },
        )
        key = json.dumps(["second.data.xml", "shared"])
        response = auth_client.get(self.endpoint, {"daq_version": "v1.0.0", "session": key})
        loader.assert_called_once_with("second.data.xml", "shared")
        assert response.context["selected_session"] == key
        assertContains(response, "/configs/second.data.xml", count=2)
        assertContains(response, "actual-detector")
        assertContains(response, "No editable copy has been created.")
        assertContains(response, "Configuration XML (read-only)")
        assertContains(response, "&lt;oks-data&gt;café&lt;/oks-data&gt;")
        assertContains(response, "&lt;/textarea&gt;&lt;script&gt;")
        assert '<script>alert("x")</script>' not in response.content.decode()
        assertContains(response, "readonly")

    @pytest.mark.parametrize(
        "error",
        [
            FileNotFoundError("missing.data.xml was not found"),
            ValueError("configuration is ambiguous"),
            RuntimeError("configuration cannot be parsed"),
        ],
    )
    def test_load_failure(self, auth_client, mocker, error):
        """Render load errors inside the HTMX replacement without stale metadata."""
        mocker.patch("drunc_ui.runconf.views.pages.load_config", side_effect=error)
        response = auth_client.get(
            self.endpoint,
            {"daq_version": "v1.0.0", "session": json.dumps(["first.data.xml", "shared"])},
            HTTP_HX_REQUEST="true",
        )
        assert response.context["selected_config"] is None
        assertContains(response, "Unable to load configuration:")
        assertContains(response, 'id="configuration-selection"')
        assert 'id="configuration-contents"' not in response.content.decode()

    def test_service_unavailable(self, auth_client, config_catalogue):
        """Surface service failures rather than showing an empty success state."""
        from grpc import RpcError

        config_catalogue.side_effect = RpcError("service unavailable")
        response = auth_client.get(
            self.endpoint,
            {"daq_version": "v1.0.0", "session": json.dumps(["first.data.xml", "shared"])},
        )
        assert response.context["selected_config"] is None
        assert response.context["selected_session"] == ""
        assertContains(response, "Unable to retrieve configurations from the SessionManager:")

    def test_no_configs(self, auth_client, config_catalogue):
        """Explain an empty service catalogue."""
        config_catalogue.return_value = []
        response = auth_client.get(self.endpoint, {"daq_version": "v1.0.0"})
        assertContains(response, "The SessionManager returned no available configurations.")

    def test_missing_release(self, auth_client, monkeypatch, config_catalogue):
        """Require a DBT release instead of inventing version data."""
        monkeypatch.delenv("SPACK_RELEASE")
        response = auth_client.get(self.endpoint)
        assert response.context["daq_versions"] == []
        assertContains(response, "SPACK_RELEASE is not set.")
        config_catalogue.assert_not_called()

    def test_initial_page_does_not_contact_service(self, auth_client, config_catalogue):
        """Only request configurations after a release is selected."""
        auth_client.get(self.endpoint)
        config_catalogue.assert_not_called()
