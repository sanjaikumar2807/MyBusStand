"""
DRF Serializers for MyBusStand API.
"""

from rest_framework import serializers
from .models import User, Location, BusRoute, Bus, Booking, ContactMessage


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'mobile', 'is_verified', 'created_at']
        read_only_fields = ['id', 'is_verified', 'created_at']


class SendOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=10, min_length=10)

    def validate_mobile(self, value):
        import re
        if not re.match(r'^[6-9]\d{9}$', value):
            raise serializers.ValidationError(
                'Please enter a valid 10-digit Indian mobile number.'
            )
        return value


class VerifyOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=10, min_length=10)
    otp = serializers.CharField(max_length=6, min_length=6)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'state', 'latitude', 'longitude']


class BusRouteSerializer(serializers.ModelSerializer):
    from_location_name = serializers.CharField(source='from_location.name', read_only=True)
    to_location_name = serializers.CharField(source='to_location.name', read_only=True)

    class Meta:
        model = BusRoute
        fields = ['id', 'from_location', 'to_location', 'from_location_name',
                  'to_location_name', 'distance_km']


class BusSerializer(serializers.ModelSerializer):
    route_display = serializers.SerializerMethodField()
    from_location = serializers.CharField(source='route.from_location.name', read_only=True)
    to_location = serializers.CharField(source='route.to_location.name', read_only=True)

    class Meta:
        model = Bus
        fields = [
            'id', 'number', 'bus_type', 'route', 'route_display',
            'from_location', 'to_location',
            'departure', 'arrival', 'duration',
            'fare', 'status', 'available_seats', 'total_seats',
        ]

    def get_route_display(self, obj):
        return f"{obj.route.from_location.name} → {obj.route.to_location.name}"


class BookingSerializer(serializers.ModelSerializer):
    bus_number = serializers.CharField(source='bus.number', read_only=True)
    bus_route = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'bus', 'bus_number', 'bus_route', 'seats',
            'pnr', 'status', 'total_fare', 'booked_at',
        ]
        read_only_fields = ['id', 'pnr', 'status', 'total_fare', 'booked_at']

    def get_bus_route(self, obj):
        return f"{obj.bus.route.from_location.name} → {obj.bus.route.to_location.name}"


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatbotSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)
    # Optional: list of previous {role, content} turns for multi-turn context
    history = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        required=False,
        default=list,
        max_length=20,
    )
