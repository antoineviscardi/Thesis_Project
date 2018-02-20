from django.views.generic.edit import FormView
from ga.models import Course, SemesterLU
from .forms import NewSemesterForm, EmailsForm
from .models import SemesterLU, Course, Assessment, Profile
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import send_mass_mail
from gams.settings import EMAIL_HOST_USER

# Create your views here.

# New Semester Views
class NewSemesterView(FormView):
    template_name = 'new_semester.html'
    form_class = NewSemesterForm
    success_url = "/admin"
    
    def form_valid(self, form):
        year = form.cleaned_data['year']
        term = form.cleaned_data['term']
        courses = Course.objects.all()
        
        cSemester = SemesterLU.objects.get_or_create(year=year, term=term)
        
        for course in courses:
            teachers = form.cleaned_data['{}'.format(course)]
            teachers = [User.objects.get(id=t) for t in teachers]
            programs = course.programs.all()
            ams = course.assessmentmethod_set.all()
            for teacher in teachers:
                for am in ams:
                    for program in programs:
                        Assessment.objects.get_or_create(
                            program=program,
                            assessmentMethod=am,
                            teacher=teacher,
                            semester=cSemester[0]
                        ) 
                
        
        return super().form_valid(form)
    
class EmailsView(FormView):
    template_name = 'emails.html'
    form_class = EmailsForm
    success_url = "/admin"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context_all = Profile.objects.all()
        context_all = [str(t.id) for t in context_all]
        context['all'] = context_all
        
        context_unsubmited = []
        for t in [p.user for p in Profile.objects.all()]:
            for a in t.assessment_set.all():
                if not(a.numOf4 and a.numOf3 and a.numOf2 and a.numOf1):
                     context_unsubmited.append(str(t.profile.id))
                     break
        context['unsubmited'] = context_unsubmited
        
        context['assigned'] = [str(Profile.objects.get(user=t).id) 
            for t in Assessment.objects.values_list(
                'teacher', 
                flat=True
            ).distinct()
        ]
        
        return context
    
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
        
        
        
