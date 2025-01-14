"""
URL configuration for Epidemic_prediction project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from Epidemic_prediction import views
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls import handler403
from django.conf.urls import handler404
from django.conf.urls import handler500

# Set the custom handler
handler403 = 'Epidemic_prediction.views.custom_permission_denied_view'
handler404 = 'Epidemic_prediction.views.custom_page_not_found_view'
handler500 = 'Epidemic_prediction.views.custom_server_error_view'


urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('admin/', admin.site.urls),
    path('', views.homePage,name='Home'),
    path('aboutUs/', views.aboutUs,name='About-Us'),
    path('mentor/', views.mentor,name='Mentor'),
    path('team/', views.team,name='Team'),
        
    path('auth/', include('signup_app.urls')),
    path('tool/', include('tool_app.urls')),
   ]