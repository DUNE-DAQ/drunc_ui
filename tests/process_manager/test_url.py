from django.test import TestCase


class TestURLs(TestCase):
    """Tests for the URLs in the process_manager app."""

    def test_boot_process_url_not_available(self):
        """Test that the boot_process URL is not included when DEBUG is False.

        NOTE That tests are always run with DEBUG=False regardless of the actual
        setting, so this test is to ensure the view does not expose debug information
        in production.
        """
        from process_manager import urls

        self.assertNotIn("boot_process", [url.pattern.name for url in urls.urlpatterns])
