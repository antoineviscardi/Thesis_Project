from django import forms
from django.contrib.auth.models import User

class EmailsForm(forms.Form):
    recipients_options = (('',''),
        ('assigned', 'teachers assigned to classes with assessments'),
        ('unsubmited', 'teachers with unsubmited assessments'),
        ('all', 'all teachers'),
    )
    
    recipients = forms.ChoiceField(
        choices=recipients_options, required=False,
        help_text='You can choose a group and modify the recipients in the list',
        widget=forms.Select(attrs={'onchange': 'updateList(this)'})
    )
    
    recipients_list = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        label="",
        help_text='Hold down "Control", or "Command" on a Mac, to select\
        more than one.'
    )
    
    object_line = forms.CharField(
        max_length=100
    )
    
    message = forms.CharField(
        widget=forms.widgets.Textarea, 
        max_length=2000,
        help_text="Use the token {{username}} to include the recipient's username"
            
    )
