"""gams URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, include
from django.contrib.auth import views as auth_views
from ga.admin import admin_site
from django.views.generic import RedirectView
 
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', RedirectView.as_view(url='login/')),
    path('login/', auth_views.login),
    path('logout/', auth_views.logout),
    path('password_reset/', auth_views.password_reset),
    path('password_reset/done/', auth_views.password_reset_done),
    path('reset/<uid64>/<token>/', auth_views.password_reset_confirm),
    path('reset/done/', auth_views.password_reset_complete),
    path('admin/', admin_site.urls),
    path('submit/', include('submit.urls')),
]
