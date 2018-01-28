from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from gamanagement.models import Profile, Department, Course, Attribute, Indicator, AssessmentMethod, Assessment

# Register your models here.

admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = Profile
    
class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline,]
    
admin.site.register(User, UserProfileAdmin)
admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Attribute)
admin.site.register(Indicator)
admin.site.register(AssessmentMethod)
admin.site.register(Assessment)
