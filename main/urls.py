"""Urls module for the main app."""

from django.urls import include, path

from .views import pages, partials

app_name = "main"

partial_urlpatterns = [
    path("messages/<str:topic>", partials.messages, name="messages"),
]

urlpatterns = [
    path("", pages.index, name="index"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("help/", pages.HelpView.as_view(), name="help"),
    path("partials/", include(partial_urlpatterns)),
]
