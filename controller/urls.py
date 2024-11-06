"""Urls module for the controller app."""

from django.urls import path

from . import views

app_name = "controller"
urlpatterns = [
    path("", views.index, name="index"),
    path("state_machine", views.state_machine, name="state_machine"),
]
