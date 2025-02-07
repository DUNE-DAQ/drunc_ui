"""Urls specific for the session manager."""

from django.urls import include, path

from .views import pages, partials

app_name = "session_manager"

partial_urlpatterns = [
    path(
        "active_sessions_table",
        partials.active_sessions_table_view,
        name="active_sessions_table",
    ),
    path(
        "available_config_table",
        partials.available_configs_table_view,
        name="available_config_table",
    ),
]

urlpatterns = [
    path("", pages.index, name="index"),
    path("partials/", include(partial_urlpatterns)),
]
