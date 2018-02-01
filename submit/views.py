from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from ga.models import Assessment, Course
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
        return self.request.user.profile.course.all()
        

class CourseDetailView(DetailView):
    model = Course
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assessments = (self.request.user.assessment_set.all()
                       .filter(course = self.object))
        
        
        # create list of forms for every assessment
        forms = []
        assessmentMethods = []
        assessmentsPk = []
        for assessment in assessments :
            forms.append(AssessmentForm(instance=assessment))
            assessmentMethods.append(assessment.assessmentMethod)
            assessmentsPk.append(assessment.pk)
            
        context['list'] = zip(assessmentMethods, forms, assessmentsPk)
        
        return context 
    
    def post(self, request, *args, **kwargs):
        assessments = self.request.user.assessment_set.all()
        instance = assessments.get(pk=request.POST['apk'])
        form = AssessmentForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('')
            
        
        
        
