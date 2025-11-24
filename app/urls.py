from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("recipient/add/", views.add_recipient, name="add_recipient"),
    path("event/add/", views.add_event, name="add_event"),
    path("event/<int:event_id>/", views.view_event, name="view_event"),
]
