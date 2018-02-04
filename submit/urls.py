from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    #path('', views.department_view),
    #path('', views.courses_view),
    path('', login_required(views.CourseListView.as_view())),
    #path('assessment/<int:pk>/', login_required(views.AssessmentUpdate.as_view()), name='assessment-update'),
    path('course/<str:pk>', login_required(views.CourseDetailView.as_view()))
]
