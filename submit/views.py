from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from gamanagement.models import Assessment
from django.views.generic.edit import UpdateView

# Create your views here. 

class AssessmentUpdate(UpdateView):
    model = Assessment
    fields = ['numOf4', 'numOf3', 'numOf2', 'numOf1']
    
@login_required
def assessments_view(request):
    assessments = request.user.assessment_set.all()
    return render(request, 'assessments.html', {'assessments':assessments})
    

    
