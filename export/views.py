from django.views.generic.edit import FormView
from .forms import ExportForm
from .export_utils import export

class ExportView(FormView):
    template_name = 'export/export.html'
    form_class = ExportForm
    success_url = "/admin"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_permission'] = True
        context['site_url'] = '/'
        return context
    
    def form_valid(self, form):
        program = form.cleaned_data['program']
        years = form.cleaned_data['years']
        
        return export(years, program)
        
        #return super().form_valid(form)
