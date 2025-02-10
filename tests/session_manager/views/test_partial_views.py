from http import HTTPStatus

from django.urls import reverse

from session_manager.tables import ActiveSessions, AvailableConfigs

from ...utils import LoginRequiredTest


class TestActiveSessionsView(LoginRequiredTest):
    """Test the controller.views.partials.active_sessions_table_view view function."""

    endpoint = reverse("session_manager:active_sessions_table")

    def test_sessions_table(self, auth_client, mocker):
        """Tests basic calls of view method."""
        mock = mocker.patch("interfaces.session_manager_interface.get_sessions")
        sessions = [{"name": "123", "actor": "Gandalf"}]
        sessions_table = ActiveSessions(sessions)
        mock.return_value = sessions

        response = auth_client.post(self.endpoint)
        assert response.status_code == HTTPStatus.OK
        actual = list(response.context["table"].as_values())
        expected = list(sessions_table.as_values())
        assert actual == expected


class TestAvailableConfigsView(LoginRequiredTest):
    """Test the controller.views.partials.available_configs_table_view view function."""

    endpoint = reverse("session_manager:available_config_table")

    def test_available_configs(self, auth_client, mocker):
        """Tests basic calls of view method."""
        mock = mocker.patch("interfaces.session_manager_interface.get_configs")
        configs = [{"file": "somewhere.xml", "id": "6x7-config"}]
        configs_table = AvailableConfigs(configs)
        mock.return_value = configs

        response = auth_client.post(self.endpoint)
        assert response.status_code == HTTPStatus.OK
        actual = list(response.context["table"].as_values())
        expected = list(configs_table.as_values())
        assert actual == expected
