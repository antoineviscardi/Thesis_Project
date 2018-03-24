from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from ga.models import Assessment, Course, SemesterLU, AssessmentMethod, Indicator
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
        return self.request.user.course_set.all()
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_permission'] = True
        return context
        

class CourseDetailView(DetailView):
    
    model = Course
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['has_permission'] = True
        
        context['introduced'] = Indicator.objects.filter(
            introduced__in=[self.object.id],
            current_flag=True
        )
        
        context['taught'] = Indicator.objects.filter(
            taught__in=[self.object.id],
            current_flag=True
        )
        
        context['utilized'] = Indicator.objects.filter(
            used__in=[self.object.id],
            current_flag=True
        )
        
        assessed = Indicator.objects.filter(
            assessed__in=[self.object.id],
            current_flag=True
        )
        context['assessed'] = assessed
        
        ams_list = [
            i.assessmentmethod_set.all() for i in assessed
        ]
        
        ass_list = [[
            Assessment.objects.filter(
                teacher=self.request.user,
                semester=SemesterLU.objects.latest(),
                assessmentMethod=am
            ) for am in am_list ] for am_list in ams_list
        ]
        
        
        tables = []
        
        for indicator in assessed:
            for am in indicator.assessmentmethod_set.filter(current_flag=True): 
                for a in am.assessment_set.filter(
                    teacher=self.request.user,
                    semester=SemesterLU.objects.latest(),
                ):
                    tables.append((
                        indicator, 
                        am, 
                        a, 
                        a.program, 
                        AssessmentForm(instance=a),
                        a.pk
                    ))
                
        context['tables'] = tables
      
        return context 
    
    def post(self, request, *args, **kwargs):
        assessments = self.request.user.assessment_set.all()
        instance = assessments.get(pk=request.POST['apk'])
        form = AssessmentForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/submit/')
            
        
        
        
