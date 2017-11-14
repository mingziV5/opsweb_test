from django.views.generic import ListView, TemplateView
from django.http import JsonResponse
from .models import SqlWorkflow, MasterConfig, SqlWorkflowStatus
from django.contrib.auth.models import Group
from .form import AddSqlWorkflow
from opsweb.utils import GetLogger
import traceback

class ListWorkflowView(ListView):
    template_name = 'workflow_list.html'
    model = SqlWorkflow
    paginate_by = 10
    before_range_num = 4
    after_range_num = 5
    ordering = 'id'

    def get_queryset(self):
        queryset = super(ListWorkflowView, self).get_queryset()
        queryset = queryset.all()
        #查询条件
        status = self.request.GET.get('status', None)
        #根据条件，筛选工单
        if status and status != 'all':
            queryset = queryset.filter(status__status_code=status)
        return queryset

    def get_page_range(self, page_obj):
        current_index = page_obj.number
        start = current_index - self.before_range_num
        end = current_index + self.after_range_num
        if start <= 0:
            start = 1
        if end > page_obj.paginator.num_pages:
            end = page_obj.paginator.num_pages
        return range(start, end+1)

    def get_context_data(self, **kwargs):
        #self.set_paginate_by(2)
        context = super(ListWorkflowView, self).get_context_data(**kwargs)
        context['page_range_obj'] = self.get_page_range(context['page_obj'])
        search_data = self.request.GET.copy()
        context['status'] = search_data.get('status', None)
        try:
            search_data.pop("page")
        except:
            pass
        context.update(search_data.dict())
        context['workflow_status'] = "&" + search_data.urlencode()
        return context

class WorkflowDetailView(TemplateView):
    template_name = 'workflow_detail.html'

    def get_context_data(self, **kwargs):
        context = super(WorkflowDetailView, self).get_context_data()
        return context

class CreateWorkflowView(TemplateView):
    template_name = 'workflow_create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateWorkflowView, self).get_context_data(**kwargs)
        context['dbs'] = MasterConfig.objects.values('cluster_name', 'db_name')
        dba_group = Group.objects.get(name='dba')
        login_user = self.request.user
        context['dbas'] = dba_group.user_set.all().exclude(username=login_user.username)
        return context

    def post(self, request):
        response = {}
        workflow_form = AddSqlWorkflow(request.POST)
        if workflow_form.is_valid():
            workflow_form_dict = workflow_form.cleaned_data
            workflow_name = workflow_form_dict.get('workflow_name')
            reviewer = workflow_form_dict.get('reviewer')
            backup = workflow_form_dict.get('backup')
            cluster_db_name = workflow_form_dict.get('cluster_db_name')
            sql_content = workflow_form_dict.get('sql_content')
            try:
                proposer = request.user.email
            except:
                GetLogger().get_logger().error(traceback.format_exc())
                response['status'] = 1
                response['errmsg'] = '登录用户身份错误'
                return JsonResponse(response)
            try:
                status = SqlWorkflowStatus.objects.get(status_name='待审核')
            except:
                GetLogger().get_logger().error(traceback.format_exc())
                response['status'] = 1
                response['errmsg'] = '获取工单初始状态出错'
            try:
                sql_obj = SqlWorkflow(workflow_name=workflow_name, reviewer=reviewer, backup=backup, cluster_db_name=cluster_db_name, sql_content=sql_content,
                                      proposer=proposer, status=status)
                sql_obj.save()
                response['status'] = 0
                return JsonResponse(response)
            except:
                GetLogger().get_logger().error(traceback.format_exc())
                response['status'] = 1
                response['errmsg'] = '新建工单出错'
        response['status'] = 1
        response['errmsg'] = '数据验证不通过'
        return JsonResponse(response)


