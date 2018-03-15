from django import forms
from ga.models import Program, SemesterLU

class ExportForm(forms.Form):

    program = forms.ModelChoiceField(
        queryset = Program.objects.all()
    )
    
    winter_semesters = SemesterLU.objects.filter(term='W')
    autumn_semesters = SemesterLU.objects.filter(term='A')
    
    yearChoices = set([int(s.year) for s in autumn_semesters])
    
    yearChoices |= set([(int(s.year) - 1) for s in winter_semesters])
    
        
    #yearChoices = set([int(s.year) for s in semesters])
    yearChoices = [(y, '{}-{}'.format(y, int(y) + 1)) for y in yearChoices]
    
    years = forms.MultipleChoiceField(
        choices = yearChoices
    )
    
    
    
