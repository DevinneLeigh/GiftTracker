from django.urls import path, include
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views

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


    path('landing/', views.landing, name='landing'),

	# a different auth system than the default Django one
	# http://localhost:8000/admin/login/?next=/admin/

	# auth system
	path('login/', auth_views.LoginView.as_view(template_name="auth/login.html"), name='user_login'),
	path('logout/', auth_views.LogoutView.as_view(), name='user_logout'),
	path('logout/', auth_views.LogoutView.as_view(template_name='auth/logged_out.html'), name='user_logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='auth/password_change_form.html'), name='user_password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='auth/password_change_done.html'), name='user_password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='auth/password_reset_form.html'), name='user_password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='user_password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), name='user_password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='user_password_reset_complete'),

	# auth registeration
	path('register/', views.register, name='user_register'),


]

