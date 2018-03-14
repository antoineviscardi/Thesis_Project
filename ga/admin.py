from django.contrib import admin
from django.db import models
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django import forms
from automated_email.views import EmailsView
from export.views import ExportView
from .views import NewSemesterView
from .forms import MyUserCreationForm, ProgramForm
from .models import (Program, Course, Attribute, 
                     Indicator, AssessmentMethod, Assessment,
                     SemesterLU)


class MyAdminSite(AdminSite):
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('new_semester/', self.admin_view(NewSemesterView.as_view())),
            path('emails/', self.admin_view(EmailsView.as_view())),
            path('export/', self.admin_view(ExportView.as_view()))
        ]
        return my_urls + urls

    
class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {
            'fields': ('username','password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        })
    )
    

MyUserAdmin.add_form = MyUserCreationForm
MyUserAdmin.add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('username', 'email', 'password1', 'password2',)
    }),
)
admin.site.unregister(User)


class CourseAdmin(admin.ModelAdmin):
    filter_horizontal = ('teachers',)

                
class AssessmentMethodInline(admin.StackedInline):
    model = AssessmentMethod
    can_delete = True
    extra = 0


class IndicatorAdmin(admin.ModelAdmin):
    list_display=('code', 'attribute', 'description')
    filter_horizontal = ('introduced', 'taught', 'used')
    exclude = ('current_flag',)
    actions = ['cease_selected']
    inlines = (AssessmentMethodInline,)
    
    def cease_selected(self, request, queryset):
        queryset.update(current_flag=False)
    
    cease_selected.short_description = 'Cease selected indicators without deleting'

    
class AttributeAdmin(admin.ModelAdmin):
    ordering = ('name',)
    exclude = ('current_flag',)
    actions = ['cease_selected']
    
    def get_queryset(self, request):
        qs = super(AttributeAdmin, self).get_queryset(request)
        return qs.filter(current_flag=True)
    
    def cease_selected(self, request, queryset):
        queryset.update(current_flag=False)
    
    cease_selected.short_description = 'Cease selected attributes without deleting'
    

class ProgramAdmin(admin.ModelAdmin):
    actions = ['cease_selected']
    
    def get_queryset(self, request):
        qs = super(ProgramAdmin, self).get_queryset(request)
        return qs.filter(current_flag=True)
        
    def get_form(self, request, obj=None, **kwargs):
        form = super(ProgramAdmin, self).get_form(request, obj, **kwargs)
        if obj is None:
            form.clean = ProgramForm.clean
        return form
    
    def cease_selected(self, request, queryset):
        prog_list = list(queryset)
        queryset.update(current_flag=False)
        print(prog_list)
        assessments = [
            a for p in prog_list for a in p.assessment_set.all().filter(
                current_flag = True
            )
        ]
        
        for a in assessments:
            a.delete()
    
    cease_selected.short_description = 'Cease selected programs without deleting'
        
        
    
class AssessmentAdmin(admin.ModelAdmin):
    fields = ('teacher', 'program', 'numOf4', 'numOf3', 'numOf2', 'numOf1')
    readonly_fields=('program', 'teacher')
    
    list_display=('pk', 'indicator', 'course', 'program', 'teacher', 'numOf4', 'numOf3', 'numOf2', 'numOf1')
    
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
 
 
admin_site = MyAdminSite(name='myadmin') 
admin_site.register(User, MyUserAdmin)
admin_site.register(Program, ProgramAdmin)
admin_site.register(Course, CourseAdmin)
admin_site.register(Attribute, AttributeAdmin)
admin_site.register(Indicator, IndicatorAdmin)
admin_site.register(Assessment, AssessmentAdmin)


