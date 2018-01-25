from django.urls import path

from . import views

urlpatterns = [
    #path('', views.department_view),
    path('', views.courses_view),
]
