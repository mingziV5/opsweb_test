from django.views.generic import ListView, TemplateView, View
from django.http import JsonResponse, QueryDict
from .models import SqlWorkflow, MasterConfig, SqlWorkflowStatus
from django.contrib.auth.models import Group
from .form import AddSqlWorkflow, CheckWorkflow
from opsweb.utils import GetLogger
from inception import inception
from inception.const import Const
import traceback, json, re, time

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
        workflow_id = self.request.GET.get('workflow_id', None)
        if workflow_id:
            try:
                sql_wf_obj = SqlWorkflow.objects.get(id=workflow_id)
                context['workflowDetail'] = sql_wf_obj
            except:
                return 'error'
        if sql_wf_obj.status.status_code in ('done', 'exception'):
            listContent = json.loads(sql_wf_obj.execute_result)
        else:
            listContent = json.loads(sql_wf_obj.review_content)
        context['listContent'] = listContent
        return context

class WorkflowCancelView(View):
    def post(self, request):
        response = {}
        workflow_id = request.POST.get('workflowid', None)
        wf_status = Const.workflow_status.get('abort')
        if not workflow_id:
            response['status'] = 1
            response['errmsg'] = '数据错误，workflow_id为空'
            return JsonResponse(response)
        workflow_id = int(workflow_id)
        wf_obj = SqlWorkflow.objects.get(id=workflow_id)
        reviewer = wf_obj.reviewer.split(',')
        #服务器端验证，如果正在执行取消动作的当前登录用户不是发起人或者审核人，报异常
        login_email = request.user.email
        if login_email is None or (login_email not in reviewer and login_email != wf_obj.proposer ):
            response['status'] = 1
            response['errmsg'] = '当前登录用户不是审核人也不是发起人，请重新登录'
            return JsonResponse(response)
        #服务器端验证，如果工单是结束状态不能结束
        if wf_obj.status.status_name in (Const.workflow_status.get('done'), Const.workflow_status.get('abort')):
            response['status'] = 1
            response['errmsg'] = '当前状态不能结束'
            return JsonResponse(response)
        try:
            wf_status_obj = SqlWorkflowStatus.objects.get(status_name=wf_status)
            wf_obj.status = wf_status_obj
            wf_obj.save()
        except:
            response['status'] = 1
            response['errmsg'] = '保存状态出错'
            return JsonResponse(response)
        response['status'] = 0
        return JsonResponse(response)

class WorkflowExecuteView(View):
    def post(self, request):
        response = {}
        workflow_id = request.POST.get('workflowid', None)
        wf_status = Const.workflow_status.get('execute')
        if not workflow_id:
            response['status'] = 1
            response['errmsg'] = '数据错误，workflow_id为空'
            return JsonResponse(response)
        workflow_id = int(workflow_id)
        wf_obj = SqlWorkflow.objects.get(id=workflow_id)
        reviewer = wf_obj.reviewer.split(',')
        login_email = request.user.email
        #服务器端验证，当前登录用户能不能执行sql
        if login_email is None or login_email not in reviewer:
            response['status'] = 1
            response['errmsg'] = '当前登录用户不是审核人，不能执行sql'
            return JsonResponse(response)
        #服务器端验证，如果工单不是待审核则不能执行
        if wf_obj.status.status_code != 'wait':
            response['status'] = 1
            response['errmsg'] = '当前工单状态不能执行sql'
            return JsonResponse(response)

        try:
            # 修改工单状态，进入执行中
            wf_obj.status = SqlWorkflowStatus.objects.get(status_name=wf_status)
            wf_obj.review_time = getNow()
            #执行之前需要重新split并check一遍，更新SHA1缓存，因为如果在执行中，其他进程去做这一步操作的话，会导致inception core dump
            inception_obj = inception.InceptionDao()
            sql_result = inception_obj.sql_auto_review(sql_content=wf_obj.sql_content, cluster_db_name=wf_obj.cluster_db_name, is_split=True)
            wf_obj.review_content = json.dumps(sql_result)
            wf_obj.save()
        except:
            GetLogger().get_logger().error(traceback.format_exc())
            response['status'] = 1
            response['errmsg'] = '执行前check出错'
            return JsonResponse(response)

        try:
            #执行sql executeStatus 0: 执行完成 1: 执行出先问题
            (execute_status, final_list) = inception_obj.sql_execute(wf_obj)

            #将执行结果存入数据库，并更新状态
            if execute_status == 1:
                wf_status = Const.workflow_status.get('exception')
                wf_obj.status = SqlWorkflowStatus.objects.get(status_name=wf_status)
                wf_obj.execute_result = json.dumps(final_list)
            else:
                wf_status = Const.workflow_status.get('done')
                wf_obj.status = SqlWorkflowStatus.objects.get(status_name=wf_status)
            wf_obj.finish_time = getNow()
            wf_obj.save()
        except:
            GetLogger().get_logger().error(traceback.format_exc())
            response['status'] = 1
            response['errmsg'] = '执行sql出错'
            return JsonResponse(response)
        response['status'] = 0
        return JsonResponse(response)

class CreateWorkflowView(TemplateView):
    template_name = 'workflow_create.html'
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace', 'check']

    def get_context_data(self, **kwargs):
        context = super(CreateWorkflowView, self).get_context_data(**kwargs)
        context['dbs'] = MasterConfig.objects.values('cluster_name', 'db_name')
        dba_group = Group.objects.get(name='dba')
        login_user = self.request.user
        #context['dbas'] = dba_group.user_set.all().exclude(username=login_user.username)
        #测试 可以选择自己
        context['dbas'] = dba_group.user_set.all()
        return context

    def check(self, request):
        response = {}
        data = QueryDict(request.body)
        checkflow_form = CheckWorkflow(data)
        if checkflow_form.is_valid():
            checkflow_form_dict = checkflow_form.cleaned_data
            sql_content = checkflow_form_dict.get('sql_content')
            cluster_db_name = checkflow_form_dict.get('cluster_db_name')
            is_split = checkflow_form_dict.get('is_split')
            is_split_flag = True if is_split=='1' else False
            #提交测试sql
            inception_obj = inception.InceptionDao()
            sql_result = inception_obj.sql_auto_review(sql_content=sql_content, cluster_db_name=cluster_db_name, is_split=is_split_flag)
            if sql_content is None or len(sql_result) == 0:
                response['status'] = 1
                response['errmsg'] = 'inception返回结果为空，可能语法错误'
                return JsonResponse(response)
            response['status'] = 0
            response['data'] = json.dumps(sql_result)
            return JsonResponse(response)
        response['status'] = 1
        response['errmsg'] = '数据审核不通过'
        return JsonResponse(response)

    def post(self, request):
        response = {}
        workflow_form = AddSqlWorkflow(request.POST)
        if workflow_form.is_valid():
            workflow_form_dict = workflow_form.cleaned_data
            workflow_name = workflow_form_dict.get('workflow_name')
            reviewer = workflow_form_dict.get('reviewer')
            backup = workflow_form_dict.get('backup')
            is_split = workflow_form_dict.get('is_split')
            is_split_flag = True if is_split=='1' else False
            cluster_db_name = workflow_form_dict.get('cluster_db_name')
            sql_content = workflow_form_dict.get('sql_content')
            workflow_status = Const.workflow_status['reviewing']
            #审核提交的sql
            inception_obj = inception.InceptionDao()
            sql_result = inception_obj.sql_auto_review(sql_content=sql_content, cluster_db_name=cluster_db_name, is_split=is_split_flag)
            if sql_result is None or len(sql_result) == 0:
                response['status'] = 1
                response['errmsg'] = 'inception返回结果为空，可能有语法错误'
                return JsonResponse(response)
            review_content = json.dumps(sql_result)
            #遍历结果sql_result判断自动审核是否通过,决定工单的状态
            flag = True
            for sql_row in sql_result:
                if isinstance(sql_row, tuple):
                    if sql_row[2] == 2:
                        flag = False
                        workflow_status = Const.workflow_status['reject']
                        break
                    elif re.match(r"\w*comments\w*", sql_row[4]):
                        flag = False
                        workflow_status = Const.workflow_status['reject']
                else:
                    if sql_result[2] == 2:
                        flag = False
                        workflow_status = Const.workflow_status['reject']
                        break
                    elif re.match(r"\w*comments\w*", sql_result[4]):
                        flag = False
                        workflow_status = Const.workflow_status['reject']
                        break
                    break

            if flag:
                workflow_status = Const.workflow_status['wait']
            try:
                proposer = request.user.email
            except:
                GetLogger().get_logger().error(traceback.format_exc())
                response['status'] = 1
                response['errmsg'] = '登录用户身份错误'
                return JsonResponse(response)
            try:
                status = SqlWorkflowStatus.objects.get(status_name=workflow_status)
            except:
                GetLogger().get_logger().error(traceback.format_exc())
                response['status'] = 1
                response['errmsg'] = '获取工单初始状态出错'
                return JsonResponse(response)
            try:
                sql_obj = SqlWorkflow(workflow_name=workflow_name, reviewer=reviewer, backup=backup, is_split=is_split,cluster_db_name=cluster_db_name, sql_content=sql_content,
                                      review_content=review_content, proposer=proposer, status=status)
                sql_obj.save()
                response['status'] = 0
                return JsonResponse(response)
            except:
                GetLogger().get_logger().error(traceback.format_exc())
                response['status'] = 1
                response['errmsg'] = '新建工单出错'
                return JsonResponse(response)
        response['status'] = 1
        response['errmsg'] = '数据验证不通过,是否;结尾'
        return JsonResponse(response)

def getNow():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

