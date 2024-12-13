from unittest import mock

from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase

from process_manager.views.partials import handle_errors


class HandleErrorsTest(TestCase):
    """Tests for the HandleErrors decorator in the process_manager views."""

    def setUp(self):
        """SetUp method to create a RequestFactory instance."""
        self.factory = RequestFactory()

    @mock.patch("logging.getLogger")
    def test_exception_view(self, mock_get_logger):
        """Test the exception_view function."""
        mock_logger = mock_get_logger.return_value

        @handle_errors
        def exception_view(request):
            raise Exception("Test exception")

        request = self.factory.get("/")
        response = exception_view(request)

        expected_content = render_to_string("main/error_message.html", request=request)
        self.assertEqual(response.content.decode(), expected_content)

        mock_logger.exception.assert_called_once()

        self.assertEqual(response.status_code, 200)
