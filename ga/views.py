from django.views.generic.edit import FormView
from ga.models import Course, SemesterLU
from .forms import NewSemesterForm
from automated_email.forms import EmailsForm
from .models import SemesterLU, Course, Assessment, Profile
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from gams.settings import EMAIL_HOST_USER

# New Semester Views
class NewSemesterView(FormView):
    template_name = 'ga/new_semester.html'
    form_class = NewSemesterForm
    success_url = "/admin"
    
    def form_valid(self, form):
        year = form.cleaned_data['year']
        term = form.cleaned_data['term']
        courses = Course.objects.all().filter(current_flag=True)
        
        cSemester = SemesterLU.objects.get_or_create(year=year, term=term)
        
        for course in courses:
            teachers = form.cleaned_data['{}'.format(course)]
            teachers = [User.objects.get(id=t) for t in teachers]
            ams = course.assessmentmethod_set.all()
            for teacher in teachers:
                for am in ams:
                    programs = am.programs.all()
                    for program in programs:
                        Assessment.objects.get_or_create(
                            program=program,
                            assessmentMethod=am,
                            teacher=teacher,
                            semester=cSemester[0]
                        ) 
                
        
        return super().form_valid(form)
    
    def form_valid(self, form):
        
        object_line=form.cleaned_data['object_line']
        message = form.cleaned_data['message']

        emails = [(
            object_line, 
            message.replace(
                '{{username}}',r.user.username
            ),
            EMAIL_HOST_USER,
            (r.user.email,)
        ) for r in form.cleaned_data['recipients_list']]   
        
        send_mass_mail(emails, fail_silently=False)
        
        return super().form_valid(form)
        
        
        
