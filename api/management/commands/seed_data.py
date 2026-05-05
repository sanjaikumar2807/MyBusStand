"""
Management command to seed the database with initial data.

Populates:
- 13 Tamil Nadu locations with coordinates
- 11 bus routes matching the existing frontend data
- 11 buses with identical details to the frontend hardcoded data
"""

from django.core.management.base import BaseCommand
from api.models import Location, BusRoute, Bus


class Command(BaseCommand):
    help = 'Seed the database with initial locations, routes, and buses'

    def handle(self, *args, **options):
        self.stdout.write('Seeding MyBusStand database...\n')

        self._seed_locations()
        self._seed_routes_and_buses()

        self.stdout.write(self.style.SUCCESS('\nDatabase seeded successfully!'))
        self.stdout.write(f'   Locations: {Location.objects.count()}')
        self.stdout.write(f'   Routes:    {BusRoute.objects.count()}')
        self.stdout.write(f'   Buses:     {Bus.objects.count()}')

    def _seed_locations(self):
        """Create 13 Tamil Nadu locations with approximate coordinates."""
        locations = [
            {'name': 'Melmaruvathur', 'latitude': 12.2333, 'longitude': 79.7333},
            {'name': 'Vandavasi', 'latitude': 12.5005, 'longitude': 79.6021},
            {'name': 'Chennai', 'latitude': 13.0827, 'longitude': 80.2707},
            {'name': 'Kanchipuram', 'latitude': 12.8342, 'longitude': 79.7036},
            {'name': 'Vellore', 'latitude': 12.9165, 'longitude': 79.1325},
            {'name': 'Tiruvannamalai', 'latitude': 12.2253, 'longitude': 79.0747},
            {'name': 'Villupuram', 'latitude': 11.9401, 'longitude': 79.4861},
            {'name': 'Puducherry', 'latitude': 11.9416, 'longitude': 79.8083},
            {'name': 'Cuddalore', 'latitude': 11.7480, 'longitude': 79.7714},
            {'name': 'Chidambaram', 'latitude': 11.3992, 'longitude': 79.6915},
            {'name': 'Mayiladuthurai', 'latitude': 11.1018, 'longitude': 79.6527},
            {'name': 'Kumbakonam', 'latitude': 10.9617, 'longitude': 79.3881},
            {'name': 'Thanjavur', 'latitude': 10.7870, 'longitude': 79.1378},
        ]

        for loc_data in locations:
            loc, created = Location.objects.get_or_create(
                name=loc_data['name'],
                defaults={
                    'state': 'Tamil Nadu',
                    'latitude': loc_data['latitude'],
                    'longitude': loc_data['longitude'],
                }
            )
            status_icon = '[NEW]' if created else '[SKIP]'
            self.stdout.write(f'  {status_icon} Location: {loc.name}')

    def _seed_routes_and_buses(self):
        """
        Create 11 routes and buses matching the existing frontend data exactly.
        Each bus entry mirrors what's hardcoded in bus listing module.html.
        """
        bus_data = [
            {
                'from': 'Melmaruvathur',
                'to': 'Vandavasi',
                'distance_km': 55.0,
                'number': 'TN-37-N-0521',
                'bus_type': 'Express',
                'departure': '06:00 AM',
                'arrival': '07:30 AM',
                'duration': '1h 30m',
                'fare': 45,
                'status': 'on-time',
                'available_seats': 22,
                'total_seats': 52,
            },
            {
                'from': 'Chennai',
                'to': 'Kanchipuram',
                'distance_km': 75.0,
                'number': 'TN-01-AN-4832',
                'bus_type': 'Volvo AC',
                'departure': '06:30 AM',
                'arrival': '08:30 AM',
                'duration': '2h 00m',
                'fare': 120,
                'status': 'on-time',
                'available_seats': 15,
                'total_seats': 45,
            },
            {
                'from': 'Kanchipuram',
                'to': 'Vellore',
                'distance_km': 120.0,
                'number': 'TN-23-BN-7156',
                'bus_type': 'AC Bus',
                'departure': '07:00 AM',
                'arrival': '09:30 AM',
                'duration': '2h 30m',
                'fare': 110,
                'status': 'on-time',
                'available_seats': 30,
                'total_seats': 50,
            },
            {
                'from': 'Vellore',
                'to': 'Tiruvannamalai',
                'distance_km': 100.0,
                'number': 'TN-23-CD-3498',
                'bus_type': 'Express',
                'departure': '07:30 AM',
                'arrival': '09:30 AM',
                'duration': '2h 00m',
                'fare': 85,
                'status': 'arriving',
                'available_seats': 10,
                'total_seats': 52,
            },
            {
                'from': 'Tiruvannamalai',
                'to': 'Villupuram',
                'distance_km': 95.0,
                'number': 'TN-06-EF-2045',
                'bus_type': 'Non-AC',
                'departure': '08:00 AM',
                'arrival': '10:00 AM',
                'duration': '2h 00m',
                'fare': 65,
                'status': 'on-time',
                'available_seats': 18,
                'total_seats': 48,
            },
            {
                'from': 'Villupuram',
                'to': 'Puducherry',
                'distance_km': 38.0,
                'number': 'TN-34-GH-6723',
                'bus_type': 'AC Bus',
                'departure': '08:30 AM',
                'arrival': '09:45 AM',
                'duration': '1h 15m',
                'fare': 55,
                'status': 'on-time',
                'available_seats': 25,
                'total_seats': 45,
            },
            {
                'from': 'Puducherry',
                'to': 'Cuddalore',
                'distance_km': 26.0,
                'number': 'PY-01-IJ-1190',
                'bus_type': 'Non-AC',
                'departure': '09:00 AM',
                'arrival': '09:50 AM',
                'duration': '0h 50m',
                'fare': 35,
                'status': 'delayed',
                'available_seats': 8,
                'total_seats': 52,
            },
            {
                'from': 'Cuddalore',
                'to': 'Chidambaram',
                'distance_km': 42.0,
                'number': 'TN-43-KL-8834',
                'bus_type': 'Express',
                'departure': '09:30 AM',
                'arrival': '10:30 AM',
                'duration': '1h 00m',
                'fare': 40,
                'status': 'on-time',
                'available_seats': 32,
                'total_seats': 52,
            },
            {
                'from': 'Chidambaram',
                'to': 'Mayiladuthurai',
                'distance_km': 40.0,
                'number': 'TN-43-MN-5567',
                'bus_type': 'Non-AC',
                'departure': '10:00 AM',
                'arrival': '11:00 AM',
                'duration': '1h 00m',
                'fare': 38,
                'status': 'on-time',
                'available_seats': 20,
                'total_seats': 48,
            },
            {
                'from': 'Mayiladuthurai',
                'to': 'Kumbakonam',
                'distance_km': 35.0,
                'number': 'TN-48-OP-4421',
                'bus_type': 'AC Bus',
                'departure': '10:30 AM',
                'arrival': '11:30 AM',
                'duration': '1h 00m',
                'fare': 50,
                'status': 'arriving',
                'available_seats': 14,
                'total_seats': 45,
            },
            {
                'from': 'Kumbakonam',
                'to': 'Thanjavur',
                'distance_km': 40.0,
                'number': 'TN-48-QR-9903',
                'bus_type': 'Volvo AC',
                'departure': '11:00 AM',
                'arrival': '11:50 AM',
                'duration': '0h 50m',
                'fare': 60,
                'status': 'on-time',
                'available_seats': 28,
                'total_seats': 45,
            },
        ]

        for entry in bus_data:
            from_loc = Location.objects.get(name=entry['from'])
            to_loc = Location.objects.get(name=entry['to'])

            route, route_created = BusRoute.objects.get_or_create(
                from_location=from_loc,
                to_location=to_loc,
                defaults={'distance_km': entry['distance_km']},
            )

            bus, bus_created = Bus.objects.get_or_create(
                number=entry['number'],
                defaults={
                    'bus_type': entry['bus_type'],
                    'route': route,
                    'departure': entry['departure'],
                    'arrival': entry['arrival'],
                    'duration': entry['duration'],
                    'fare': entry['fare'],
                    'status': entry['status'],
                    'available_seats': entry['available_seats'],
                    'total_seats': entry['total_seats'],
                },
            )

            route_icon = '[NEW]' if route_created else '[SKIP]'
            bus_icon = '[NEW]' if bus_created else '[SKIP]'
            self.stdout.write(
                f'  {route_icon} Route: {route} | '
                f'{bus_icon} Bus: {bus.number} ({bus.bus_type})'
            )
