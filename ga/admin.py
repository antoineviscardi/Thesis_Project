from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .forms import IndicatorCourseAdminForm
from .models import (Profile, Department, Course, Attribute, 
                     Indicator, AssessmentMethod, Assessment,
                     )

# Register your models here.

admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    
class UserProfileAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    fieldsets = (
        (None, {
            'fields': ('username','password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
    )

class AdminCourse(admin.ModelAdmin):
    model = Course
    filter_horizontal = ('teachers',)
'''
class IndicatorCourseInline(admin.TabularInline):
    model = Indicator_Course
    form = IndicatorCourseAdminForm
    can_delete = False
'''
class IndicatorAdmin(admin.ModelAdmin):
    #inlines = (IndicatorCourseInline,)
    filter_horizontal = ('introduced', 'taught', 'used')
  
admin.site.register(User, UserProfileAdmin)
admin.site.register(Department)
admin.site.register(Course, AdminCourse)
admin.site.register(Attribute)
admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(AssessmentMethod)
admin.site.register(Assessment)
