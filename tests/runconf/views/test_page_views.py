"""Tests for runconf page views."""

import html
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
    """Mock list_production_configs."""
    return mocker.patch(
        "drunc_ui.runconf.views.pages.list_production_configs", return_value=LISTING
    )


@pytest.fixture(autouse=True)
def config_copy(mocker):
    """Mock get_production_config."""

    def get_copy(file, session_id):
        return {
            "file": file,
            "session_id": session_id,
            "path": f"/prod/{file}",
            "working_path": f"/work/{file}",
            "contents": "<oks-data/>",
            "tree": {
                "id": session_id,
                "class": "Session",
                "state": "INCLUDED",
                "relations": {
                    "segment": [
                        {
                            "id": 'café</textarea><script>alert("x")</script>',
                            "class": "Segment",
                            "state": "EXCLUDED",
                            "relations": {},
                        }
                    ]
                },
            },
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
        assertContains(response, "Select a configuration to view its tree.")
        assert 'id="configuration-tree"' not in response.content.decode()
        content = response.content.decode()
        session_select = content.split('id="daqSession"', 1)[1].split(">", 1)[0]
        assert "disabled" in session_select
        assert "required" in session_select

    def test_selects_not_restored_by_browser(self, auth_client: Client) -> None:
        """Stop browsers restoring stale selections the server didn't render."""
        content = auth_client.get(self.endpoint, {"daq_version": "v1.0.0"}).content.decode()
        version_select = content.split('id="daqVersion"', 1)[1].split(">", 1)[0]
        session_select = content.split('id="daqSession"', 1)[1].split(">", 1)[0]
        assert 'autocomplete="off"' in version_select
        assert 'autocomplete="off"' in session_select
        # If the shown version still differs from the rendered one, resync on load.
        assert 'data-selected="v1.0.0"' in version_select
        assert "load[this.value !== this.dataset.selected]" in version_select

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
        """Request the selected file and session, and show its tree as JSON read-only."""
        key = json.dumps(["second.data.xml", "shared"])
        response = auth_client.get(self.endpoint, {"daq_version": "v1.0.0", "session": key})
        config_copy.assert_called_once_with("second.data.xml", "shared")
        assert response.context["selected_session"] == key
        assertContains(response, '<th scope="row">Apparatus</th>')
        assertContains(response, "<td>np02</td>")
        assertContains(response, "/prod/second.data.xml", count=1)
        assertContains(response, "/work/second.data.xml", count=1)
        textarea = response.content.decode().split('id="configuration-tree"', 1)[1]
        assert "readonly" in textarea.split(">", 1)[0]
        tree = textarea.split(">", 1)[1].split("</textarea>", 1)[0]
        assert (
            json.loads(html.unescape(tree))
            == config_copy.side_effect("second.data.xml", "shared")["tree"]
        )
        assert "&quot;state&quot;: &quot;EXCLUDED&quot;" in tree
        assert "café&lt;/textarea&gt;&lt;script&gt;" in tree
        assert "alert(" not in response.content.decode().replace(tree, "")

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

    def test_options_disabled_without_config(self, auth_client: Client) -> None:
        """Only Help is usable until a configuration is loaded."""
        content = auth_client.get(self.endpoint, {"daq_version": "v1.0.0"}).content.decode()
        assert "disabled" in _button(content, "create-run-config")
        assert "disabled" in _button(content, "reset")
        assert "disabled" not in _button(content, "help")

    def test_options_enabled_with_config(self, auth_client: Client) -> None:
        """Create and Reset become usable once a configuration is loaded."""
        response = auth_client.get(self.endpoint, SELECTION)
        content = response.content.decode()
        for button_id in ("create-run-config", "help", "reset"):
            assert "disabled" not in _button(content, button_id)

    def test_reset_reloads_selection(self, auth_client: Client) -> None:
        """Reset re-requests the page with the current version and session."""
        content = auth_client.get(self.endpoint, SELECTION).content.decode()
        reset = _button(content, "reset")
        assert f'hx-get="{self.endpoint}"' in reset
        assert 'hx-include="#daqVersion, #daqSession"' in reset

    def test_modals_rendered(self, auth_client: Client) -> None:
        """Render the help modal and the create confirmation modal."""
        content = auth_client.get(self.endpoint).content.decode()
        assert 'id="createConfigModal"' in content
        assert 'id="helpModal"' in content
        assert "Welcome to the Run Configuration Editor" in content
        confirm = _button(content, "confirm-create-run-config")
        assert f'hx-post="{reverse("runconf:create_config")}"' in confirm
        assert "X-CSRFToken" in confirm


SELECTION = {"daq_version": "v1.0.0", "session": json.dumps(["second.data.xml", "shared"])}


def _button(content: str, button_id: str) -> str:
    """Return the opening tag attributes of the button with ``button_id``."""
    return content.split(f'id="{button_id}"', 1)[1].split(">", 1)[0]


@pytest.fixture
def created(mocker):
    """Mock create_run_config."""
    return mocker.patch(
        "drunc_ui.runconf.views.pages.create_run_config",
        return_value={
            "session_id": "shared",
            "source_path": "/work/second.data.xml",
            "path": "/run/np02_now.data.xml",
            "drunc_command": "drunc-unified-shell ssh-standalone /run/np02_now.data.xml shared x",
        },
    )


class TestCreateConfigView(LoginRequiredTest):
    """Test the run configuration creation view."""

    endpoint = reverse("runconf:create_config")

    def test_get_not_allowed(self, auth_client: Client) -> None:
        """Only POST creates a run configuration."""
        response = auth_client.get(self.endpoint, SELECTION)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED

    def test_create(self, auth_client: Client, created) -> None:
        """Create from the selected working copy and show the result."""
        response = auth_client.post(self.endpoint, SELECTION)
        created.assert_called_once_with("/work/second.data.xml", "shared")
        assertTemplateUsed(response, "runconf/config_view.html")
        assert response.context["selected_session"] == SELECTION["session"]
        modal = response.content.decode().split('id="createdConfigModal"', 1)[1]
        assert "/work/second.data.xml" in modal
        assert "bootstrap.Modal.getOrCreateInstance" in modal
        content = response.content.decode()
        # htmx only swaps #configuration-selection, so the popup must be inside it.
        assert content.index('id="createdConfigModal"') < content.index('id="createConfigModal"')
        assertContains(response, "/run/np02_now.data.xml")
        assertContains(response, "drunc-unified-shell ssh-standalone")

    @pytest.mark.parametrize(
        ("selection", "error"),
        [
            ({}, "Select a configuration before creating a run configuration."),
            ({"daq_version": "v1.0.0"}, "Select a configuration before creating"),
            ({"daq_version": "invalid"}, "Select an available DAQ version."),
            (
                {"daq_version": "v1.0.0", "session": "invalid"},
                "Select an available session for this DAQ version.",
            ),
        ],
    )
    def test_invalid_selection(
        self, auth_client: Client, created, selection: dict[str, str], error: str
    ) -> None:
        """Refuse to create without a valid loaded configuration."""
        response = auth_client.post(self.endpoint, selection)
        created.assert_not_called()
        assertContains(response, error)
        assert 'id="createdConfigModal"' not in response.content.decode()
