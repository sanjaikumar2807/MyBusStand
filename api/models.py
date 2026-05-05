"""
Database models for the MyBusStand API.

Models:
- User: OTP-based authentication (mobile number as identifier)
- Location: 13 Tamil Nadu locations for route autocomplete
- BusRoute: Route definitions between two locations
- Bus: Individual bus schedule entries
- Booking: Ticket booking records with PNR
- ContactMessage: Contact form submissions
"""

import random
import string
from django.db import models
from django.utils import timezone
from datetime import timedelta


class User(models.Model):
    """OTP-based user authentication model (no passwords)."""
    mobile = models.CharField(max_length=10, unique=True, db_index=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"+91 {self.mobile}"

    def generate_otp(self):
        """Generate a 6-digit OTP and set 5-minute expiry."""
        self.otp = str(random.randint(100000, 999999))
        self.otp_expiry = timezone.now() + timedelta(minutes=5)
        self.save()
        return self.otp

    def verify_otp(self, otp):
        """Verify OTP validity and expiry."""
        if self.otp == otp and self.otp_expiry and self.otp_expiry > timezone.now():
            self.is_verified = True
            self.otp = None
            self.otp_expiry = None
            self.save()
            return True
        return False


class Location(models.Model):
    """Tamil Nadu locations for autocomplete and route search."""
    name = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=50, default='Tamil Nadu')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class BusRoute(models.Model):
    """Route definitions between two locations."""
    from_location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='routes_from'
    )
    to_location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='routes_to'
    )
    distance_km = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('from_location', 'to_location')
        ordering = ['from_location__name']

    def __str__(self):
        return f"{self.from_location.name} -> {self.to_location.name}"


class Bus(models.Model):
    """Individual bus with schedule, type, and fare information."""
    BUS_TYPES = [
        ('Express', 'Express'),
        ('AC Bus', 'AC Bus'),
        ('Non-AC', 'Non-AC'),
        ('Volvo AC', 'Volvo AC'),
    ]

    STATUS_CHOICES = [
        ('on-time', 'On Time'),
        ('delayed', 'Delayed'),
        ('arriving', 'Arriving'),
    ]

    number = models.CharField(max_length=20, unique=True)
    bus_type = models.CharField(max_length=20, choices=BUS_TYPES)
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='buses')
    departure = models.CharField(max_length=10)  # e.g. "06:00 AM"
    arrival = models.CharField(max_length=10)      # e.g. "07:30 AM"
    duration = models.CharField(max_length=10)     # e.g. "1h 30m"
    fare = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='on-time')
    available_seats = models.IntegerField(default=30)
    total_seats = models.IntegerField(default=52)

    class Meta:
        verbose_name_plural = 'Buses'
        ordering = ['departure']

    def __str__(self):
        return f"{self.number} ({self.route})"


class Booking(models.Model):
    """Ticket booking record."""
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bookings')
    seats = models.IntegerField(default=1)
    pnr = models.CharField(max_length=10, unique=True, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='confirmed')
    total_fare = models.IntegerField(default=0)
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booked_at']

    def __str__(self):
        return f"PNR: {self.pnr} - {self.user.mobile}"

    def save(self, *args, **kwargs):
        if not self.pnr:
            self.pnr = self._generate_pnr()
        if not self.total_fare:
            self.total_fare = self.bus.fare * self.seats
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_pnr():
        """Generate a unique 10-character PNR code."""
        return 'MBS' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))


class ContactMessage(models.Model):
    """Contact form submissions from the website."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}: {self.subject}"
