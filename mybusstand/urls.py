"""
URL configuration for mybusstand project.
Serves both the API endpoints and the frontend HTML pages.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from django.http import HttpResponse
from os import path

def serve_frontend(request, path_url='index.html'):
    """Fallback function to serve frontend files directly from the Frontend folder."""
    # Ensure the path is correct relative to BASE_DIR
    from django.conf import settings
    full_path = path.join(settings.BASE_DIR, 'Frontend', path_url)
    try:
        with open(full_path, 'rb') as f:
            return HttpResponse(f.read(), content_type='text/html')
    except FileNotFoundError:
        return HttpResponse(f'File {path_url} not found in Frontend directory', status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

    # Frontend pages
    path('', serve_frontend, name='home'),
    path('index.html', serve_frontend, name='index'),
    path('login/', TemplateView.as_view(template_name='user authentication module.html'), name='login'),
    path('user authentication module.html', TemplateView.as_view(template_name='user authentication module.html'), name='auth'),
    path('route search module.html', TemplateView.as_view(template_name='route search module.html'), name='route-search'),
    path('bus listing module.html', TemplateView.as_view(template_name='bus listing module.html'), name='bus-listing'),
    path('live bus tracking module.html', TemplateView.as_view(template_name='live bus tracking module.html'), name='live-tracking'),
    path('chatbot support module.html', TemplateView.as_view(template_name='chatbot support module.html'), name='chatbot'),

    # Direct links
    path('driver/', TemplateView.as_view(template_name='driver.html'), name='driver-page'),
    path('passenger/', TemplateView.as_view(template_name='passenger.html'), name='passenger-page'),
]
