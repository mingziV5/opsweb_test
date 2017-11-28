from django.conf.urls import url, include
from inception import views

urlpatterns = [
    url(r'^workflowlist/$', views.ListWorkflowView.as_view(), name='inception_workflow_list'),
    url(r'^detail/$', views.WorkflowDetailView.as_view(), name='inception_workflow_detail'),
    url(r'^create/$', views.CreateWorkflowView.as_view(), name='inception_workflow_create'),
    url(r'^cancel/$', views.WorkflowCancelView.as_view(), name='inception_workflow_cancel'),
]