from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def grade_submission(request):
    if request.method == "POST":
        MyGradeForm = GradeForm(request.POST)
        if MyGradeForm.is_valid():
            numOf4 = MyGradeFrom.cleaned_data['numOf4']
            numOf3 = MyGradeFrom.cleaned_data['numOf3']
            numOf2 = MyGradeFrom.cleaned_data['numOf2']
            numOf1 = MyGradeFrom.cleaned_data['numOf1']
    return HttpResponse("Submission  here")
    
@login_required
def department_view(request):
    department = request.user.profile.departmentID.name
    return HttpResponse(department)
    
@login_required
def courses_view(request):
    
    courses = request.user.course_set.all()
        
    return render(request, 'courses.html', {'courses':courses})
