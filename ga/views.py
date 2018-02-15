from django.views.generic.edit import FormView
from ga.models import Course, SemesterLU
from .forms import NewSemesterForm, EmailsForm
from .models import SemesterLU, Course, Assessment
from django.contrib.auth.models import User

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
    
    
    
