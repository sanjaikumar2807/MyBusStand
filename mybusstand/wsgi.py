"""
WSGI config for mybusstand project.
"""

import os
import logging
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mybusstand.settings')
application = get_wsgi_application()

# Automatically run database migrations & seed data on startup (essential for Render)
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    call_command('seed_data')
except Exception as e:
    logging.getLogger(__name__).warning(f"Startup migration/seed notice: {e}")
