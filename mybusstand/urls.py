"""
URL configuration for mybusstand project.
Serves both the API endpoints and the frontend HTML pages.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

    # Frontend pages served via Django Templates
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('index.html', TemplateView.as_view(template_name='index.html'), name='index'),
    path('login/', TemplateView.as_view(template_name='user authentication module.html'), name='login'),
    path('user authentication module.html', TemplateView.as_view(template_name='user authentication module.html'), name='auth'),
    path('route search module.html', TemplateView.as_view(template_name='route search module.html'), name='route-search'),
    path('bus listing module.html', TemplateView.as_view(template_name='bus listing module.html'), name='bus-listing'),
    path('live bus tracking module.html', TemplateView.as_view(template_name='live bus tracking module.html'), name='live-tracking'),
    path('chatbot support module.html', TemplateView.as_view(template_name='chatbot support module.html'), name='chatbot'),

    # Direct links for driver and passenger
    path('driver/', TemplateView.as_view(template_name='driver.html'), name='driver-page'),
    path('passenger/', TemplateView.as_view(template_name='passenger.html'), name='passenger-page'),
]
