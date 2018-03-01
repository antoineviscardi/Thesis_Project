from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from ga.models import Assessment, Course, SemesterLU, AssessmentMethod
from ga.forms import AssessmentForm
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.template.defaulttags import register

# Create your views here. 

class AssessmentUpdate(UpdateView):
    model = Assessment
    fields = ['numOf4', 'numOf3', 'numOf2', 'numOf1']


class CourseListView(ListView):
    def get_queryset(self):
        return self.request.user.profile.course_set.all()
        

class CourseDetailView(DetailView):
    
    model = Course
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        ams = AssessmentMethod.objects.all().filter(
            course=self.object
        )
        
        assessments = [
            am.assessment_set.all().filter(
                teacher=self.request.user,
                semester=SemesterLU.objects.latest()
            ) for am in ams
        ]
        
        apks = [[a.pk for a in _a] for _a in assessments]
        forms = [[AssessmentForm(instance=a) for a in _a] for _a in assessments]
        
        forms_apks_zip = [zip(f,a) for f,a in zip(forms, apks)]
        
        context['list'] = zip(ams, forms_apks_zip)
        
        return context 
    
    def post(self, request, *args, **kwargs):
        assessments = self.request.user.assessment_set.all()
        instance = assessments.get(pk=request.POST['apk'])
        form = AssessmentForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('')
            
        
        
        
