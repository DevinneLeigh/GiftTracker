from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),

    # Recipients
    path("recipient/add/", views.add_recipient, name="add_recipient"),
    path("recipient/<int:id>/edit/", views.edit_recipient, name="edit_recipient"),
    path("recipient/<int:id>/delete/", views.delete_recipient, name="delete_recipient"),

    # Events
    path("event/add/", views.add_event, name="add_event"),
    path("event/<int:id>/edit/", views.edit_event, name="edit_event"),
    path("event/<int:id>/delete/", views.delete_event, name="delete_event"),
    path("event/<int:id>/", views.view_event, name="view_event"),
]
