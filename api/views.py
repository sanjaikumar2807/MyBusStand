"""
API Views for MyBusStand.

Endpoints:
- Auth: send-otp, verify-otp, logout
- Locations: list all locations
- Routes: search buses by from/to
- Buses: list, detail, tracking
- Bookings: create, list user bookings
- Contact: submit contact form
- Chatbot: OpenAI GPT-powered assistant with keyword fallback
- Bus Location: live GPS coordinates for a bus (simulated)
"""

import random
import math
import time
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.db.models import Q

from .models import User, Location, BusRoute, Bus, Booking, ContactMessage
from .serializers import (
    SendOTPSerializer, VerifyOTPSerializer, UserSerializer,
    LocationSerializer, BusRouteSerializer, BusSerializer,
    BookingSerializer, ContactMessageSerializer, ChatbotSerializer,
)


# ──────────────────────────────────────────────────────────────────────────────
# AUTH ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    """Generate & store OTP for a mobile number. Returns OTP in demo mode."""
    serializer = SendOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    mobile = serializer.validated_data['mobile']
    user, created = User.objects.get_or_create(mobile=mobile)
    otp = user.generate_otp()

    return Response({
        'success': True,
        'message': 'OTP sent successfully',
        'otp': otp,  # Exposed for demo — remove in production
        'mobile': mobile,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verify OTP and return auth token on success."""
    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    mobile = serializer.validated_data['mobile']
    otp = serializer.validated_data['otp']

    try:
        user = User.objects.get(mobile=mobile)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found. Please request OTP first.',
        }, status=status.HTTP_404_NOT_FOUND)

    if user.verify_otp(otp):
        # Create or retrieve a DRF auth token
        # We use Django's built-in User model for token auth, but since we have
        # a custom User, we'll use a simulated token approach
        token_key = _generate_token(mobile)
        return Response({
            'success': True,
            'message': 'OTP verified successfully',
            'token': token_key,
            'mobile': mobile,
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
            'message': 'Invalid or expired OTP',
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_view(request):
    """Invalidate session (client should discard token)."""
    return Response({
        'success': True,
        'message': 'Logged out successfully',
    }, status=status.HTTP_200_OK)


def _generate_token(mobile):
    """Generate a simple token for demo purposes."""
    import hashlib
    import time
    raw = f"{mobile}-{time.time()}-{random.randint(1000, 9999)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:40]


# ──────────────────────────────────────────────────────────────────────────────
# LOCATION ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def location_list(request):
    """List all locations for autocomplete."""
    locations = Location.objects.all()
    serializer = LocationSerializer(locations, many=True)
    return Response(serializer.data)


# ──────────────────────────────────────────────────────────────────────────────
# ROUTE SEARCH ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def route_search(request):
    """Search buses on a route given `from` and `to` query params."""
    from_name = request.query_params.get('from', '').strip()
    to_name = request.query_params.get('to', '').strip()

    if not from_name or not to_name:
        return Response({
            'error': 'Both "from" and "to" query parameters are required.',
        }, status=status.HTTP_400_BAD_REQUEST)

    # Find buses matching the route (case-insensitive)
    buses = Bus.objects.filter(
        route__from_location__name__iexact=from_name,
        route__to_location__name__iexact=to_name,
    ).select_related('route__from_location', 'route__to_location')

    serializer = BusSerializer(buses, many=True)
    return Response({
        'from': from_name,
        'to': to_name,
        'count': buses.count(),
        'buses': serializer.data,
    })


# ──────────────────────────────────────────────────────────────────────────────
# BUS ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def bus_list(request):
    """
    List all buses. Supports optional query filters:
    - bus_type: AC, Non-AC, Volvo, Express
    - max_fare: maximum fare threshold
    - sort: departure (default), fare, duration
    """
    buses = Bus.objects.select_related(
        'route__from_location', 'route__to_location'
    ).all()

    # Filters
    bus_type = request.query_params.get('bus_type', '')
    max_fare = request.query_params.get('max_fare', '')
    sort_by = request.query_params.get('sort', 'departure')

    if bus_type:
        buses = buses.filter(bus_type__icontains=bus_type)

    if max_fare:
        try:
            buses = buses.filter(fare__lte=int(max_fare))
        except ValueError:
            pass

    # Sorting
    if sort_by == 'fare':
        buses = buses.order_by('fare')
    elif sort_by == 'duration':
        buses = buses.order_by('duration')
    else:
        buses = buses.order_by('departure')

    serializer = BusSerializer(buses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def bus_detail(request, bus_id):
    """Get details of a single bus by ID."""
    try:
        bus = Bus.objects.select_related(
            'route__from_location', 'route__to_location'
        ).get(id=bus_id)
    except Bus.DoesNotExist:
        return Response({
            'error': 'Bus not found.',
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = BusSerializer(bus)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def bus_track(request, bus_id):
    """
    Simulated live tracking data for a bus.
    Returns randomized position, speed, ETA, and next-stop info.
    """
    try:
        bus = Bus.objects.select_related(
            'route__from_location', 'route__to_location'
        ).get(id=bus_id)
    except Bus.DoesNotExist:
        return Response({
            'error': 'Bus not found.',
        }, status=status.HTTP_404_NOT_FOUND)

    from_name = bus.route.from_location.name
    to_name = bus.route.to_location.name

    # Simulated tracking data (same logic as frontend)
    progress = random.randint(10, 90)
    speed = random.randint(30, 60)
    eta_minutes = max(2, round((100 - progress) * 0.3))
    distance_to_next = round(random.uniform(0.5, 4.0), 1)
    passengers = random.randint(15, bus.total_seats)

    return Response({
        'bus_id': bus.id,
        'bus_number': bus.number,
        'route': f"{from_name} → {to_name}",
        'from_location': from_name,
        'to_location': to_name,
        'progress_percent': progress,
        'current_speed_kmh': speed,
        'eta_minutes': eta_minutes,
        'distance_to_next_stop_km': distance_to_next,
        'passengers': passengers,
        'total_seats': bus.total_seats,
        'status': bus.status,
    })


# ──────────────────────────────────────────────────────────────────────────────
# BOOKING ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def create_booking(request):
    """Create a new booking. Requires bus ID, seats, and mobile."""
    bus_id = request.data.get('bus')
    seats = request.data.get('seats', 1)
    mobile = request.data.get('mobile', '')

    if not bus_id or not mobile:
        return Response({
            'error': 'bus and mobile are required.',
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        bus = Bus.objects.get(id=bus_id)
    except Bus.DoesNotExist:
        return Response({
            'error': 'Bus not found.',
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        user = User.objects.get(mobile=mobile)
    except User.DoesNotExist:
        return Response({
            'error': 'User not found. Please login first.',
        }, status=status.HTTP_404_NOT_FOUND)

    seats = int(seats)
    if seats > bus.available_seats:
        return Response({
            'error': f'Only {bus.available_seats} seats available.',
        }, status=status.HTTP_400_BAD_REQUEST)

    booking = Booking.objects.create(
        user=user,
        bus=bus,
        seats=seats,
    )

    # Reduce available seats
    bus.available_seats -= seats
    bus.save()

    serializer = BookingSerializer(booking)
    return Response({
        'success': True,
        'message': 'Booking confirmed!',
        'booking': serializer.data,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def booking_list(request):
    """List bookings for a user (by mobile query param)."""
    mobile = request.query_params.get('mobile', '')

    if not mobile:
        return Response({
            'error': 'mobile query parameter is required.',
        }, status=status.HTTP_400_BAD_REQUEST)

    bookings = Booking.objects.filter(
        user__mobile=mobile
    ).select_related('bus__route__from_location', 'bus__route__to_location')

    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)


# ──────────────────────────────────────────────────────────────────────────────
# CONTACT ENDPOINT
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def contact_submit(request):
    """Submit a contact form message."""
    serializer = ContactMessageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        serializer.save()
    except Exception as e:
        # Database table may not exist yet — run: python manage.py migrate
        import logging
        logging.getLogger(__name__).error(f'contact_submit DB error: {e}')
        return Response({
            'success': False,
            'message': 'Database not initialised. Run: python manage.py migrate',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({
        'success': True,
        'message': 'Message sent successfully! We will get back to you within 24 hours.',
    }, status=status.HTTP_201_CREATED)


# ──────────────────────────────────────────────────────────────────────────────
# CHATBOT ENDPOINT
# ──────────────────────────────────────────────────────────────────────────────

# Chatbot keyword responses (same as frontend chatbot module)
CHATBOT_RESPONSES = {
    'bus routes': 'I can help you find bus routes between any two locations. Just tell me your source and destination, or use our route search feature for detailed options.',
    'ticket prices': 'Bus fares vary based on distance and bus type. AC buses cost ₹65-120, Non-AC buses cost ₹30-80, and Volvo buses cost ₹85-150. Exact fare depends on your route.',
    'bus timings': 'Buses typically run from 6:00 AM to 11:00 PM. Peak hours have more frequent buses - every 10-15 minutes. Off-peak frequency is every 30-45 minutes.',
    'live tracking': 'You can track any bus in real-time! After selecting your bus, click the "Track Bus" button to see live location, ETA, and journey progress.',
    'refund policy': 'Full refund is available if cancelled 2 hours before departure. 50% refund for cancellations 1 hour before. No refund for cancellations less than 1 hour before departure.',
    'contact support': 'You can reach our support team at 📞 1800-123-4567 (24/7) or email support@mybusstand.com. We typically respond within 2 hours.',
    'booking': 'To book a ticket: 1) Search your route 2) Select preferred bus 3) Choose seats 4) Make payment 5) Receive confirmation SMS with ticket details.',
    'cancellation': 'Go to "My Bookings" in your profile, select the ticket to cancel, and click "Cancel". Refund will be processed according to our policy.',
    'payment': 'We accept all major credit/debit cards, UPI (PhonePe, GPay, Paytm), net banking, and digital wallets. Cash payment available at select bus stands.',
    'lost ticket': "Don't worry! Go to \"My Bookings\" and download your ticket again. You can also show the confirmation SMS at the bus stand.",
    'delay': 'If your bus is delayed, you can track it live for updated ETA. For delays over 30 minutes, you can request a voucher for future travel.',
    'help': "I'm here to help! You can ask me about routes, timings, fares, booking, tracking, or any other bus-related questions.",
}

# Additional keyword mappings for broader matching
KEYWORD_MAP = {
    'route': 'bus routes',
    'from': 'bus routes',
    'to': 'bus routes',
    'price': 'ticket prices',
    'fare': 'ticket prices',
    'cost': 'ticket prices',
    'time': 'bus timings',
    'schedule': 'bus timings',
    'when': 'bus timings',
    'track': 'live tracking',
    'location': 'live tracking',
    'where': 'live tracking',
    'book': 'booking',
    'reservation': 'booking',
    'ticket': 'booking',
    'cancel': 'cancellation',
    'refund': 'cancellation',
    'pay': 'payment',
    'lost': 'lost ticket',
    'missing': 'lost ticket',
    'late': 'delay',
}


# ── OpenAI system prompt ──────────────────────────────────────────────────────
MYBUSSTAND_SYSTEM_PROMPT = """
You are a helpful customer support assistant for MyBusStand, a bus booking platform
operating across Tamil Nadu, India. You help users with:
- Searching bus routes between cities/towns in Tamil Nadu
- Checking bus timings, fares, and availability
- Booking tickets and managing reservations (PNR lookup, seat selection)
- Live bus tracking and ETA information
- Cancellations and the refund policy
- Payment methods (UPI, cards, net banking, wallets, cash)
- Lost tickets and re-downloading passes
- General travel guidance

Key policies:
- Full refund if cancelled 2+ hours before departure
- 50% refund if cancelled 1–2 hours before departure
- No refund within 1 hour of departure
- Support line: 1800-123-4567 (24/7), email: support@mybusstand.com

Bus types and typical fares:
- Non-AC Express: ₹30–80
- AC Sleeper: ₹65–120
- Volvo Multi-Axle: ₹85–150

Be concise, friendly, and always respond in English unless the user writes in Tamil.
If you cannot help with something, politely direct the user to the support line.
""".strip()


def _keyword_fallback(message: str) -> dict:
    """Original keyword-based logic used as a fallback when OpenAI is unavailable."""
    msg = message.lower()
    for key, response in CHATBOT_RESPONSES.items():
        if key in msg:
            return {'response': response, 'matched_topic': key}
    for keyword, topic in KEYWORD_MAP.items():
        if keyword in msg:
            return {'response': CHATBOT_RESPONSES[topic], 'matched_topic': topic}
    return {
        'response': (
            f'I understand you\'re asking about "{message}". '
            'I can help you with bus routes, timings, fares, booking, tracking, and more. '
            'Could you please be more specific or try one of the quick help options?'
        ),
        'matched_topic': None,
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot_response(request):
    """
    AI-powered chatbot using OpenAI GPT-4o-mini.
    Accepts:
      { "message": "<user text>", "history": [{"role": "user/assistant", "content": "..."}] }
    Falls back to keyword matching if the OpenAI call fails.
    """
    import logging
    logger = logging.getLogger(__name__)

    serializer = ChatbotSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user_message = serializer.validated_data['message']
    history      = serializer.validated_data.get('history', [])

    # ── Build message list for OpenAI ────────────────────────────────────────
    messages = [{'role': 'system', 'content': MYBUSSTAND_SYSTEM_PROMPT}]

    # Attach previous turns (max last 10 pairs = 20 messages)
    for turn in history[-20:]:
        role    = turn.get('role', '').strip()
        content = turn.get('content', '').strip()
        if role in ('user', 'assistant') and content:
            messages.append({'role': role, 'content': content})

    messages.append({'role': 'user', 'content': user_message})

    # ── Call OpenAI ──────────────────────────────────────────────────────────
    try:
        from django.conf import settings
        from openai import OpenAI

        client   = OpenAI(api_key=settings.OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=400,
            temperature=0.7,
        )
        ai_reply = completion.choices[0].message.content.strip()
        return Response({
            'response':      ai_reply,
            'matched_topic': 'openai',
            'model':         completion.model,
        })

    except Exception as exc:
        logger.warning('OpenAI chatbot call failed, using keyword fallback: %s', exc)
        fallback = _keyword_fallback(user_message)
        fallback['fallback'] = True
        return Response(fallback)


# ──────────────────────────────────────────────────────────────────────────────
# BUS LIVE LOCATION ENDPOINT
# ──────────────────────────────────────────────────────────────────────────────

# Chennai-area route waypoints (lat, lng)
_ROUTE_WAYPOINTS = [
    (13.0827, 80.2707),  # Chennai Central
    (13.0500, 80.2100),  # Tambaram
    (12.9250, 80.1240),  # Chengalpattu
    (12.8200, 79.7000),  # Kanchipuram
    (12.7400, 79.0700),  # Vellore-ish direction
]


@api_view(['GET'])
@permission_classes([AllowAny])
def bus_location(request, bus_id=None):
    """
    Return simulated live GPS coordinates for a bus.
    The position oscillates slowly along a predefined route based on
    the current time, so repeated calls return smoothly moving coordinates.
    """
    # Use time to produce a slowly changing progress (full loop every 10 minutes)
    t = time.time()
    cycle = 600  # seconds for a full back-and-forth
    progress = (t % cycle) / cycle  # 0.0 → 1.0

    # Interpolate along waypoints
    num_segments = len(_ROUTE_WAYPOINTS) - 1
    seg_progress = progress * num_segments
    seg_index = min(int(seg_progress), num_segments - 1)
    seg_frac = seg_progress - seg_index

    lat1, lng1 = _ROUTE_WAYPOINTS[seg_index]
    lat2, lng2 = _ROUTE_WAYPOINTS[seg_index + 1]

    lat = lat1 + (lat2 - lat1) * seg_frac
    lng = lng1 + (lng2 - lng1) * seg_frac

    # Add tiny jitter so marker wiggles realistically
    lat += math.sin(t * 0.7) * 0.0005
    lng += math.cos(t * 0.5) * 0.0005

    speed = round(random.uniform(28, 62), 1)
    eta   = max(2, round((1.0 - progress) * 90))

    return Response({
        'bus_id':   bus_id,
        'lat':      round(lat, 6),
        'lng':      round(lng, 6),
        'speed':    speed,
        'eta_min':  eta,
        'progress': round(progress * 100, 1),
    })
