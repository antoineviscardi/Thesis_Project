from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from main.models import Profile, Department

# Register your models here.

admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = Profile
    
class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline,]
    
admin.site.register(User, UserProfileAdmin)
admin.site.register(Department)
