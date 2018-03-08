from django.views.generic.edit import FormView
from .forms import ExportForm
from .export_utils import export
# Create your views here.

class ExportView(FormView):
    template_name = 'export/export.html'
    form_class = ExportForm
    success_url = "/admin"
    
    def form_valid(self, form):
        program = form.cleaned_data['program']
        years = form.cleaned_data['years']
        
        export(years, program)
        
        return super().form_valid(form)
