"""
URL configuration for mybusstand project.
Serves both the API endpoints and the frontend HTML pages.
"""

import os
from django.contrib import admin
from django.urls import path, include
from django.http import FileResponse, Http404
from django.conf import settings


def serve_frontend(request, page='index.html'):
    """Serve frontend HTML files directly (bypassing template engine to avoid
    conflicts with JavaScript template literals like ${...})."""
    frontend_dir = settings.BASE_DIR.parent / 'Frontend'
    file_path = frontend_dir / page

    if file_path.exists() and file_path.is_file():
        return FileResponse(open(file_path, 'rb'), content_type='text/html')
    raise Http404(f'Page not found: {page}')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

    # Frontend page routes — served as raw HTML files
    path('', serve_frontend, name='home'),
    path('index.html', serve_frontend, {'page': 'index.html'}, name='index'),
    path('login', serve_frontend, {'page': 'user authentication module.html'}, name='login'),
    path('user authentication module.html', serve_frontend, {'page': 'user authentication module.html'}, name='auth'),
    path('route search module.html', serve_frontend, {'page': 'route search module.html'}, name='route-search'),
    path('bus listing module.html', serve_frontend, {'page': 'bus listing module.html'}, name='bus-listing'),
    path('live bus tracking module.html', serve_frontend, {'page': 'live bus tracking module.html'}, name='live-tracking'),
    path('chatbot support module.html', serve_frontend, {'page': 'chatbot support module.html'}, name='chatbot'),
]
