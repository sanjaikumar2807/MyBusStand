"""
Django admin registration for MyBusStand models.
"""

from django.contrib import admin
from .models import User, Location, BusRoute, Bus, Booking, ContactMessage


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['mobile', 'is_verified', 'created_at']
    list_filter = ['is_verified']
    search_fields = ['mobile']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'latitude', 'longitude']
    search_fields = ['name']


@admin.register(BusRoute)
class BusRouteAdmin(admin.ModelAdmin):
    list_display = ['from_location', 'to_location', 'distance_km']
    list_filter = ['from_location', 'to_location']


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ['number', 'bus_type', 'route', 'departure', 'arrival', 'fare', 'status']
    list_filter = ['bus_type', 'status']
    search_fields = ['number']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['pnr', 'user', 'bus', 'seats', 'total_fare', 'status', 'booked_at']
    list_filter = ['status']
    search_fields = ['pnr', 'user__mobile']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at']
    search_fields = ['name', 'email', 'subject']
