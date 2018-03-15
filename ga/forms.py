from ga.models import SEASON_CHOICES, Assessment, Indicator, Course, SemesterLU, AssessmentMethod, Program, Attribute, Course
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import datetime


class MyUserCreationForm(UserCreationForm):
 
    def __init__(self, *args, **kwargs):
        super(MyUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'
        self.fields['email'] = forms.EmailField(
            label="E-mail", 
            max_length=75
        )
        
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = super(MyUserCreationForm, self).clean_password2()
        if bool(password1) ^ bool(password2):
            raise forms.ValidationError("Fill out both fields")
        return password2


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['numOf4', 'numOf3', 'numOf2', 'numOf1']
        labels = {
            'numOf4': _('Exceeds Expectations - 4'),
            'numOf3': _('Meets Expectations - 3'),
            'numOf2': _('Needs Improvement - 2'),
            'numOf1': _('Unacceptable - 1'),
        }
        
class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        exclude = ('current_flag',)
    
    def clean(self):
        name = self.cleaned_data['name']
        try:
            prog = Program.objects.get(name=name)
            if prog.current_flag is True:
                raise forms.ValidationError('Program with this Name already exists.')
        except Program.DoesNotExist:
            pass
        return self.cleaned_data
        

class AssessmentMethodForm(forms.ModelForm):
    class Meta:
        model = AssessmentMethod
        exclude = ('current_flag',)
        
    def clean(self):
        try:
            am = AssessmentMethod.objects.get(
                indicator = self.cleaned_data['indicator'],
                course = self.cleaned_data['course'],
                criteria = self.cleaned_data['criteria'],
                expectation4 = self.cleaned_data['expectation4'],
                expectation3 = self.cleaned_data['expectation3'],
                expectation2 = self.cleaned_data['expectation2'],
                expectation1 = self.cleaned_data['expectation1'],
                time_year = self.cleaned_data['time_year'],
                time_semester = self.cleaned_data['time_semester'],
                assessment_medium = self.cleaned_data['assessment_medium']
            )
            if am.current_flag is True:
                raise forms.ValidationError(
                    'This Assessment method already exists.'
                )
        except AssessmentMethod.DoesNotExist:
            pass
        
        return self.cleaned_data


class IndicatorForm(forms.ModelForm):
    class Meta:
        model = Indicator
        exclude = ('current_flag',)
    
    def clean(self):
        try:
            i = Indicator.objects.get(
                code = self.cleaned_data['code']
            )
            self.instance = i
            if i.current_flag is True:
                raise forms.ValidationError(
                    'Indicator with this Code already exists.'
                )
        except Indicator.DoesNotExist:
            pass
        
        return self.cleaned_data
        

class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        exclude = ('current_flag',)
    
    def clean(self):
        try:
            a = Attribute.objects.get(
                code = self.cleaned_data['code']
            )
            self.instance = a
            if a.current_flag is True:
                raise forms.ValidationError(
                    'Attribute with this Code already exists.'
                )
        except Attribute.DoesNotExist:
            pass
            
        return self.cleaned_data
        

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ('current_flag',)
    
    def clean(self):
        try:
            c = Course.objects.get(
                code = self.cleaned_data['code']
            )
            self.instance = c
            if c.current_flag is True:
                raise forms.ValidationError(
                    'Course with this Code already exists.'
                )
        except Course.DoesNotExist:
            pass
        
        return self.cleaned_data
     
    
class NewSemesterForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(NewSemesterForm, self).__init__(*args, **kwargs)
        
        cYear = datetime.datetime.now().year
        cTerm = SemesterLU.objects.latest().term
        iTerm = "A" if cTerm=="W" else "W"
        yearChoices = [(y,y) for y in range(cYear-5, cYear+3)]
        
        self.fields['year'] = forms.ChoiceField(
            choices=yearChoices, initial=cYear)
        self.fields['term'] = forms.ChoiceField(
            choices=SEASON_CHOICES, initial=iTerm)
        
        courses = Course.objects.all()
        teachers = User.objects.all()
        teachersID = [t.id for t in teachers]
        
        for course in courses:
            self.fields['{}'.format(course)] = forms.MultipleChoiceField(
                choices=zip(teachersID, teachers), required=False)
            self.fields['{}'.format(course)].label = '{}'.format(course)
        
    def clean(self):
        cleaned_data = super().clean()
        year = cleaned_data['year']
        term = cleaned_data['term']
        if SemesterLU.objects.filter(year=year, term=term).exists():
            raise forms.ValidationError(
                "This semester already exists."
            )
        
