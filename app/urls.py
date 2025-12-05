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
    path("participant/<int:participant_id>/move_wishlist/", views.move_wishlist_to_gifts, name="move_wishlist_to_gifts"),



    # Wish List
    path('recipient/<int:recipient_id>/add_wish_list/', views.add_wish_list, name='add_wish_list'),
    path("wishlist/<int:wish_id>/edit/", views.edit_wish_list, name="edit_wish_list"),
    path('<int:wishlist_id>/<str:name>/wishlist/', views.view_wish_list, name='view_wish_list'),
    path("wishlist/<int:id>/delete/", views.delete_wish_list, name="delete_wish_list"),
    path("wishlist/bulk_delete/", views.bulk_delete_wish_list, name="bulk_delete_wish_list"),

    # Add/Edit/Delete WishList URLs
    # path('recipient/<int:recipient_id>/wishlist/', views.view_wish_list, name='view_wish_list'),
    # path('recipient/<int:recipient_id>/add_wish_list/', views.add_wish_list, name='add_wish_list'),
    # path('wishlist/<int:wish_id>/edit/', views.edit_wish_list, name='edit_wish_list'),
    # path('wishlist/<int:id>/delete/', views.delete_wish_list, name='delete_wish_list'),
    # path('wishlist/bulk_delete/', views.bulk_delete_wish_list, name='bulk_delete_wish_list'),



    # Participants
    path("event/<int:event_id>/add-participant/", views.add_participant, name="add_participant"),
    path("participant/<int:participant_id>/edit/", views.edit_participant, name="edit_participant"),
    path("participant/<int:id>/delete/", views.delete_participant, name="delete_participant"),


    #Gifts
    path("participant/<int:participant_id>/add-gift/", views.add_gift, name="add_gift"),
    path("participant/<int:gift_id>/edit-gift", views.edit_gift, name="edit_gift"),
    path("gift/<int:id>/delete/", views.delete_gift, name="delete_gift"),


    # new shared AJAX endpoint for scraping
    path('scrape-product/', views.scrape_product_ajax, name='scrape_product_ajax'),


]

