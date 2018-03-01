from django.contrib import admin
from django.db import models
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.urls import path
from django import forms
from .views import NewSemesterView, EmailsView
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

class MyUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(MyUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'
        self.fields['email'] = forms.EmailField(
            label="E-mail", 
            max_length=75
        )
        
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = super(MyUserCreationForm, self).clean_password2()
        if bool(password1) ^ bool(password2):
            raise forms.ValidationError("Fill out both fields")
        return password2

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

UserProfileAdmin.add_form = MyUserCreationForm
UserProfileAdmin.add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('username', 'email', 'password1', 'password2',)
    }),
)
admin.site.unregister(User)

class CourseAdmin(admin.ModelAdmin):
    filter_horizontal = ('teachers',)
    exclude = ('current_flag',)
                
class AssessmentMethodInline(admin.StackedInline):
    model = AssessmentMethod
    exclude = ('current_flag',)
    filter_horizontal = ('programs',)
    can_delete = False
    extra = 1

class IndicatorAdmin(admin.ModelAdmin):
    filter_horizontal = ('introduced', 'taught', 'used')
    exclude = ('current_flag',)
    inlines = (AssessmentMethodInline,)
    
class AttributeAdmin(admin.ModelAdmin):
    exclude = ('current_flag',)
    ordering = ('name',)
    
class AssessmentAdmin(admin.ModelAdmin):
    fields = ('teacher', 'program', 'numOf4', 'numOf3', 'numOf2', 'numOf1')
    readonly_fields=('program', 'teacher')
    
    list_display=('pk', 'indicator', 'course', 'program', 'profile', 'numOf4', 'numOf3', 'numOf2', 'numOf1')
  
    def profile(self, obj):
        return obj.teacher.profile
    profile.short_description = 'Teacher'
    profile.admin_order_field = 'teacher__profile'
    
    def course(self, obj):
        return obj.assessmentMethod.course
    course.admin_order_field = 'assessmentMethod__course'
       
    def indicator(self, obj):
        return obj.assessmentMethod.indicator
    indicator.admin_order_field = 'assessmentMethod__indicator'
    
    def get_actions(self, request):
        actions = super(AssessmentAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_add_permission(self, request, obj=None):
        return False
        
    def get_queryset(self, request):
        qs = super(AssessmentAdmin, self).get_queryset(request)
        return qs.filter(semester=SemesterLU.objects.latest())
  
admin_site.register(User, UserProfileAdmin)
admin_site.register(Program)
admin_site.register(Course, CourseAdmin)
admin_site.register(Attribute, AttributeAdmin)
admin_site.register(Indicator, IndicatorAdmin)
admin_site.register(Assessment, AssessmentAdmin)
