"""URL configuration for runconf app."""

from django.urls import path

from drunc_ui.runconf.views import pages

app_name = "runconf"

urlpatterns = [
    path("", pages.config_view, name="config_view"),
]
