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

    # Wish List
    path('recipient/<int:recipient_id>/add_wish_list/', views.add_wish_list, name='add_wish_list'),
    path('recipient/<int:recipient_id>/view_wish_list/', views.view_wish_list, name='view_wish_list'),
    path("wishlist/<int:id>/delete/", views.delete_wish_list, name="delete_wish_list"),
    # path("wishlist/<int:id>/edit/", views.edit_wish_list, name="edit_wish_list"),
    path("wishlist/bulk_delete/", views.bulk_delete_wish_list, name="bulk_delete_wish_list"),



    # Participants
    path("event/<int:event_id>/add-participant/", views.add_participant, name="add_participant"),
    path("participant/<int:participant_id>/edit/", views.edit_participant, name="edit_participant"),
    path("participant/<int:id>/delete/", views.delete_participant, name="delete_participant"),
]
