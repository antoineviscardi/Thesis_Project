from django import forms
from ga.models import Program, SemesterLU

class ExportForm(forms.Form):

    program = forms.ModelChoiceField(
        queryset = Program.objects.all()
    )
    
    semesters = SemesterLU.objects.all()
    yearChoices = set([int(s.year) for s in semesters])
    yearChoices = [(y, '{}-{}'.format(y, int(y) + 1)) for y in yearChoices]
    
    years = forms.MultipleChoiceField(
        choices = yearChoices
    )
    
    
    
