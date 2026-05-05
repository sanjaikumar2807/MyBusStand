"""
WSGI config for mybusstand project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mybusstand.settings')
application = get_wsgi_application()
