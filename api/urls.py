"""
URL routing for MyBusStand API.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/send-otp/', views.send_otp, name='send-otp'),
    path('auth/verify-otp/', views.verify_otp, name='verify-otp'),
    path('auth/logout/', views.logout_view, name='logout'),

    # Locations
    path('locations/', views.location_list, name='location-list'),

    # Route Search
    path('routes/search/', views.route_search, name='route-search'),

    # Buses
    path('buses/', views.bus_list, name='bus-list'),
    path('buses/<int:bus_id>/', views.bus_detail, name='bus-detail'),
    path('buses/<int:bus_id>/track/', views.bus_track, name='bus-track'),
    path('buses/<int:bus_id>/location/', views.bus_location, name='bus-location'),

    # Bookings
    path('bookings/', views.booking_list, name='booking-list'),
    path('bookings/create/', views.create_booking, name='booking-create'),

    # Contact
    path('contact/', views.contact_submit, name='contact-submit'),

    # Chatbot
    path('chatbot/', views.chatbot_response, name='chatbot'),
]
