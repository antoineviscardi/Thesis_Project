from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    #path('', views.department_view),
    #path('', views.courses_view),
    path('', views.assessments_view, name='assessments-view'),
    path('assessment/<int:pk>/', login_required(views.AssessmentUpdate.as_view()), name='assessment-update')
]
