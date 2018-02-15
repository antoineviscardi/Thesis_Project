from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from .views import NewSemesterView, EmailsView
from .forms import IndicatorCourseAdminForm
from .models import (Profile, Program, Course, Attribute, 
                     Indicator, AssessmentMethod, Assessment,
                     SemesterLU)

class MyAdminSite(AdminSite):
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('new_semester/', self.admin_view(NewSemesterView.as_view())),
            path('emails/', self.admin_view(EmailsView.as_view())),
        ]
        return my_urls + urls

admin_site = MyAdminSite(name='myadmin')


# Register your models here.

#admin_site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    filter_horizontal  = ('program',)

class ProfileCourseInline(admin.StackedInline):
    model = Course.teachers.through
    
class UserProfileAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    fieldsets = (
        (None, {
            'fields': ('username','password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        })
    )

class CourseAdmin(admin.ModelAdmin):
    filter_horizontal = ('teachers','programs')
    exclude = ('current_flag',)
                
class AssessmentMethodInline(admin.StackedInline):
    model = AssessmentMethod
    exclude = ('current_flag',)
    can_delete = False
    extra = 1

class IndicatorAdmin(admin.ModelAdmin):
    filter_horizontal = ('introduced', 'taught', 'used')
    exclude = ('current_flag',)
    inlines = (AssessmentMethodInline,)
    
class AttributeAdmin(admin.ModelAdmin):
    exclude = ('current_flag',)
    
class AssessmentAdmin(admin.ModelAdmin):
    fields = ('teacher', 'program', 'numOf4', 'numOf3', 'numOf2', 'numOf1')
    readonly_fields=('program', 'teacher')

  
admin_site.register(User, UserProfileAdmin)
admin_site.register(Program)
admin_site.register(Course, CourseAdmin)
admin_site.register(Attribute, AttributeAdmin)
admin_site.register(Indicator, IndicatorAdmin)
admin_site.register(Assessment, AssessmentAdmin)
