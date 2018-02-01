from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .forms import IndicatorCourseAdminForm
from .models import (Profile, Department, Course, Attribute, 
                     Indicator, AssessmentMethod, Assessment,
                     SemesterLU)

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
    
    def save_model(self, request, obj, form, change):
        teachers = obj.teachers.all()
        currentSemester = SemesterLU.objects.latest()
        depts = obj.department.all()
        ams = obj.assessmentmethod_set.all()
        
        ''' Create assessment for teacher assigned to the course
        '''
        
        for teacher in teachers:
            for am in ams:
                for dept in depts:
                    Assessment.objects.get_or_create(
                        department=dept,
                        assessmentMethod=am,
                        teacher=teacher.user,
                        semester=currentSemester
                    )
                    

        ''' If a teacher is unasigned, delete the assessments
        only if they are empty
        '''
        if 'teachers' in form.changed_data:
            for am in ams :
                assessments = Assessment.objects.filter(
                    semester=currentSemester,
                    assessmentMethod=am
                    )
                for assessment in assessments :
                    if teacher not in teachers :
                        if (assessment.numOf4 or assessment.numOf3 
                            or assessment.numOf2 or assessment.numOf1) :
                            assessment.delete() 
 
        super().save_model(request, obj, form, change) 
                
                                                              

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
