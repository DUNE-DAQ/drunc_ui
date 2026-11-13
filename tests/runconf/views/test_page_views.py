"""Tests for runconf page views."""

import json
from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from ...utils import LoginRequiredTest

LISTING = {
    "daq_version": "v1.0.0",
    "apparatus": "np02",
    "configs": [
        {"file": "first.data.xml", "session_id": "shared", "path": "/prod/first.data.xml"},
        {"file": "second.data.xml", "session_id": "shared", "path": "/prod/second.data.xml"},
        {"file": "first.data.xml", "session_id": "another", "path": "/prod/first.data.xml"},
    ],
}


@pytest.fixture(autouse=True)
def listing(mocker):
    """Stand in for the proposed list_production_configs endpoint."""
    return mocker.patch(
        "drunc_ui.runconf.views.pages.list_production_configs", return_value=LISTING
    )


@pytest.fixture(autouse=True)
def config_copy(mocker):
    """Stand in for the proposed get_production_config endpoint."""

    def get_copy(file, session_id):
        return {
            "file": file,
            "session_id": session_id,
            "path": f"/prod/{file}",
            "working_path": f"/work/{file}",
            "contents": '<oks-data>café</oks-data></textarea><script>alert("x")</script>',
        }

    return mocker.patch("drunc_ui.runconf.views.pages.get_production_config", side_effect=get_copy)


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
                {
                    "daq_version": "v1.0.0",
                    "session": json.dumps(["appSession.data.xml", "test-session"]),
                },
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

    def test_load_selection(self, auth_client: Client, config_copy) -> None:
        """Request the selected file and session, and show the working copy read-only."""
        key = json.dumps(["second.data.xml", "shared"])
        response = auth_client.get(self.endpoint, {"daq_version": "v1.0.0", "session": key})
        config_copy.assert_called_once_with("second.data.xml", "shared")
        assert response.context["selected_session"] == key
        assertContains(response, '<th scope="row">Apparatus</th>')
        assertContains(response, "<td>np02</td>")
        assertContains(response, "/prod/second.data.xml", count=1)
        assertContains(response, "/work/second.data.xml", count=1)
        assertContains(response, "&lt;oks-data&gt;café&lt;/oks-data&gt;")
        assertContains(response, "&lt;/textarea&gt;&lt;script&gt;")
        assert '<script>alert("x")</script>' not in response.content.decode()
        textarea = response.content.decode().split('id="configuration-contents"', 1)[1]
        assert "readonly" in textarea.split(">", 1)[0]

    def test_no_copy_without_selection(self, auth_client: Client, config_copy) -> None:
        """Only request a working copy once a session is selected."""
        auth_client.get(self.endpoint, {"daq_version": "v1.0.0"})
        config_copy.assert_not_called()

    def test_missing_apparatus(self, auth_client: Client, listing) -> None:
        """Say when no apparatus is reported."""
        listing.return_value = {**LISTING, "apparatus": ""}
        response = auth_client.get(
            self.endpoint,
            {"daq_version": "v1.0.0", "session": json.dumps(["first.data.xml", "shared"])},
        )
        assertContains(response, "<td>Not set</td>")
