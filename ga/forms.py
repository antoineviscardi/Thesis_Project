from ga.models import Assessment, Indicator, Course
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _

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
        
class IndicatorCourseAdminForm(forms.ModelForm):
    class Meta:
        model = Indicator
        fields = ['course']
     
    course = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name='Introduced in',
            is_stacked=False
        )
    )
    '''
    def __inti__(self, *args, **kwargs):
        super(IndicatorCourseAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['course'].initial = self.instance.course_set.all()
    '''
    '''
    def save(self, commit=True):
        indicator = super(IndicatorAdminForm, self).save(commit=False)
        if commit:
            indicator.save()
        if indicator.pk:
            indicator.introduced_set = self.cleaned_data['userprofiles']
            self.save_m2m()
        return indicator
    '''
