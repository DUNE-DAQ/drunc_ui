"""Urls module for the controller app."""

from django.urls import include, path

from .views import pages, partials

app_name = "controller"

partial_urlpatterns = [
    path("state_machine", partials.state_machine, name="state_machine"),
    path("dialog", partials.dialog, name="dialog"),
    path("app_tree_summary", partials.app_tree_view_summary, name="app_tree_summary"),
    path("app_tree_table", partials.app_tree_view_table, name="app_tree_table"),
    path(
        "active_sessions_table",
        partials.active_sessions_table_view,
        name="active_sessions_table",
    ),
    path(
        "available_config",
        partials.available_configs_table_view,
        name="available_config",
    ),
]

urlpatterns = [
    path("", pages.index, name="index"),
    path("app_tree", pages.app_tree_view, name="app_tree"),
    path("ers_logs", pages.ers_logs, name="ers_logs"),
    path("sessions", pages.session_manager_view, name="session_manager"),
    path("partials/", include(partial_urlpatterns)),
]
