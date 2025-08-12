from django.test import TestCase


class TestURLs(TestCase):
    """Tests for the URLs in the process_manager app."""

    def test_url_in_debug(self):
        """Test that the boot_process URL is included when DEBUG is True."""
        from process_manager import urls

        with self.settings(DEBUG=True):
            self.assertIn("boot_process", [url.name for url in urls.urlpatterns])

        with self.settings(DEBUG=False):
            self.assertNotIn("boot_process", [url.name for url in urls.urlpatterns])
