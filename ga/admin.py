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

class CourseAdmin(admin.ModelAdmin):
    filter_horizontal = ('teachers','department')
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

  
admin.site.register(User, UserProfileAdmin)
admin.site.register(Department)
admin.site.register(Course, CourseAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Indicator, IndicatorAdmin)
admin.site.register(Assessment)
