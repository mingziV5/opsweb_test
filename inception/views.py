from django.views.generic import ListView, TemplateView
from .models import SqlWorkflow

class ListWorkflowView(ListView):
    template_name = 'workflow_list.html'
    model = SqlWorkflow

class WorkflowDetailView(TemplateView):
    template_name = 'workflow_detail.html'

class CreateWorkflowView(TemplateView):
    template_name = 'workflow_create.html'
