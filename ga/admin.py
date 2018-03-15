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
from .forms import (MyUserCreationForm, ProgramForm, AssessmentMethodForm, 
                    IndicatorForm, AttributeForm, CourseForm)
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
    actions = ('cease_selected',)
    filter_horizontal = ('teachers',)
    exclude = ('current_flag',)
    
    def get_queryset(self, request):
        qs = super(CourseAdmin, self).get_queryset(request)
        return qs.filter(current_flag=True)
        
    def get_form(self, request, obj=None, **kwargs):
        form = super(CourseAdmin, self).get_form(request, obj, **kwargs)
        if obj is None:
            form.clean = CourseForm.clean
        return form
    
    def cease_selected(self, request, queryset):
        course_list = queryset.all()
        ams = AssessmentMethod.objects.all().filter(
            course__in=course_list,
        )
        AssessmentMethodAdmin.cease_selected(AssessmentMethodAdmin, request, ams)
        for course in queryset.all():
            c = Course.objects.all().filter(id=course.id)
            c.update(current_flag=False)

    cease_selected.short_description = 'Cease selected courses without deleting'           
    

class AssessmentMethodAdmin(admin.ModelAdmin):
    exclude = ('current_flag',)
    actions = ('cease_selected',)
    list_display=(
        'pk', 'indicator', 'course', 
        'time_year', 'time_semester'
    )
    
    def get_queryset(self, request):
        qs = super(AssessmentMethodAdmin, self).get_queryset(request)
        return qs.filter(current_flag=True)
        
    def get_form(self, request, obj=None, **kwargs):
        form = super(AssessmentMethodAdmin, self).get_form(request, obj, **kwargs)
        if obj is None:
            form.clean = AssessmentMethodForm.clean
        return form
        
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'indicator':
            kwargs['queryset'] = Indicator.objects.all().filter(current_flag=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def cease_selected(self, request, queryset):
        am_list = queryset.all()
        assessments = set([
            a for am in am_list for a in am.assessment_set.all().filter(
                semester = SemesterLU.objects.latest()
            )
        ])
        
        for a in assessments:
            a.delete();
        
        queryset.update(current_flag=False)
        
    cease_selected.short_description = 'Cease selected assessment methods without deleting'


class IndicatorAdmin(admin.ModelAdmin):
    filter_horizontal = ('introduced', 'taught', 'used')
    actions = ['cease_selected']
    exclude = ('current_flag',)
    
    def get_queryset(self, request):
        qs = super(IndicatorAdmin, self).get_queryset(request)
        return qs.filter(current_flag=True)
        
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            form = super(IndicatorAdmin, self).get_form(request, obj, **kwargs)
            form.clean = IndicatorForm.clean
            return form
        else:
            return super(IndicatorAdmin, self).get_form(request, obj, **kwargs)
    
    def cease_selected(self, request, queryset):
        indicator_list = queryset.all()
        ams = AssessmentMethod.objects.all().filter(
            indicator__in=indicator_list,
        )  
        AssessmentMethodAdmin.cease_selected(AssessmentMethodAdmin, request, ams)
        for indicator in queryset.all():
            ind = Indicator.objects.all().filter(id=indicator.id)
            ind.update(current_flag=False)
            
        
    
    cease_selected.short_description = 'Cease selected indicators without deleting'
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'programs':
            kwargs['queryset'] = Program.objects.all().filter(current_flag=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)
        
    
class AttributeAdmin(admin.ModelAdmin):
    ordering = ('name',)
    exclude = ('current_flag',)
    actions = ['cease_selected']
    
    def get_queryset(self, request):
        qs = super(AttributeAdmin, self).get_queryset(request)
        return qs.filter(current_flag=True)
        
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            form = super(AttributeAdmin, self).get_form(request, obj, **kwargs)
            form.clean = AttributeForm.clean
            return form
        else:
            return super(AttributeAdmin, self).get_form(request, obj, **kwargs)
    
    def cease_selected(self, request, queryset):
        attribute_list = queryset.all()
        indicator_list = Indicator.objects.all().filter(
            attribute__in=attribute_list
        )
        IndicatorAdmin.cease_selected(IndicatorAdmin, request, indicator_list)
        for attribute in queryset:
            att = Attribute.objects.all().filter(id=attribute.id)
            att.update(current_flag=False)
        print(indicator_list.all())
    
    cease_selected.short_description = 'Cease selected attributes without deleting'
    

class ProgramAdmin(admin.ModelAdmin):
    actions = ['cease_selected']
    exclude = ('current_flag',)
    
    def get_queryset(self, request):
        qs = super(ProgramAdmin, self).get_queryset(request)
        return qs.filter(current_flag=True)
        
    def get_form(self, request, obj=None, **kwargs):
        form = super(ProgramAdmin, self).get_form(request, obj, **kwargs)
        if obj is None:
            form.clean = ProgramForm.clean
        return form
    
    def cease_selected(self, request, queryset):
        prog_list = queryset.all()
        assessments = set([
            a for p in prog_list for a in p.assessment_set.all().filter(
                semester = SemesterLU.objects.latest()
            )
        ])
        
        for a in assessments:
            a.delete()    
        
        for program in queryset:
            prog = Program.objects.all().filter(id=program.id)
            prog.update(current_flag=False)
       
            for i in Indicator.programs.through.objects.all().filter(program=program):
                i.delete()
    
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
admin_site.register(AssessmentMethod, AssessmentMethodAdmin)
admin_site.register(Assessment, AssessmentAdmin)


