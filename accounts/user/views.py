from django.views.generic import View, TemplateView, ListView
from django.contrib.auth import authenticate, login, logout
from django.http.response import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.http import QueryDict
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from permissions.mixins import MyPermissionRequiredMixin
from opsweb.utils import GetLogger
import traceback

class UserLoginView(View):
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username = username, password = password)
        response = {'status': 0, 'errmsg': ''}
        if user:
            login(request, user)
            response['next_url'] = request.GET.get('next') if request.GET.get('next', None) else '/'
        else:
            response['status'] = 1
            response['errmsg'] = '用户名密码错误'
        return JsonResponse(response)

    def get(self, request, *args, **kwargs):
        return render(request, 'public/login.html')

class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('user_login'))

    def post(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('user_login'))

class UserLoginTplView(TemplateView):
    template_name = 'public/login.html'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        response = {'status': 0}
        if user:
            login(request, user)
            response['next_url'] = request.GET.get('next') if request.GET.get('next', None) else '/'
        else:
            response['status'] = 1
            response['errmsg'] = '用户名密码错误'
        return JsonResponse(response)

class UserlogoutTplView(TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('user_login'))

class UserListView(LoginRequiredMixin, ListView):
    '''
    template_name = 'user/userlist.html'
    model = User
    paginate_by = 10
    before_range_num = 4
    after_range_num = 5
    
    def get_queryset(self):
        queryset = super(UserListView, self).get_queryset()
        queryset = queryset.filter(is_superuser=False)
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
        context = super(UserListView, self).get_context_data(**kwargs)
        context['page_range_obj'] = self.get_page_range(context['page_obj'])
        return context
    '''
    template_name = 'user/userlist.html'
    model = User
    paginate_by = 10
    before_range_num = 4
    after_range_num = 5
    ordering = 'id'

    def get_queryset(self):
        queryset = super(UserListView, self).get_queryset()
        queryset = queryset.filter(is_superuser=False)
        #查询条件
        username = self.request.GET.get('username', None)
        if username:
            queryset = queryset.filter(username__contains=username)
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
        self.set_paginate_by(2)
        context = super(UserListView, self).get_context_data(**kwargs)
        context['page_range_obj'] = self.get_page_range(context['page_obj'])

        #处理查询条件
        search_data = self.request.GET.copy()
        try:
            search_data.pop("page")
        except:
            pass
        context.update(search_data.dict())
        context['search_data'] = "&" + search_data.urlencode()
        return context

    def set_paginate_by(self, user_paginate_by):
        if user_paginate_by:
            self.paginate_by = user_paginate_by

    #权限验证，类视图，需要装饰在view的get方法上，没有get方法重写get方法
    @method_decorator(permission_required("auth.add_user",login_url=reverse_lazy("error" ,kwargs={"next":"index", "msg":"没有相应的权限"})))
    def get(self, request, *args, **kwargs):
        return super(UserListView, self).get(request, *args, **kwargs)

class ModifyUserStatusView(LoginRequiredMixin, View):

    def post(self, request):
        response = {}
        if request.user.has_perm('auth.change_user'):
            uid = request.POST.get('uid', None)
            try:
                user_obj = User.objects.get(id=uid)
                if user_obj.is_active:
                    user_obj.is_active = False
                else:
                    user_obj.is_active = True
                user_obj.save()
                response['status'] = 0
            except User.DoesNotExist:
                response['status'] = 1
                response['errmsg'] = "用户不存在"
            return JsonResponse(response)
        else:
            response['status'] = 1
            response['errmsg'] = "没有操作用户的权限"
            return JsonResponse(response)

class ModifyUserGroupView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.has_perm('auth.change_user'):
            uid = request.GET.get('uid', None)
            group_objs = Group.objects.all()
            try:
                user_obj = User.objects.get(id=uid)
            except User.DoesNotExist:
                pass
            else:
                group_objs = group_objs.exclude(id__in=user_obj.groups.values_list('id'))
            return JsonResponse(list(group_objs.values('id', 'name')), safe=False)
        else:
            return JsonResponse({'status': 1, 'errmsg': '没有操作用户的权限'})

    def put(self, request):
        response = {'status': 0}
        if request.user.has_perm('auth.change_user'):
            data = QueryDict(request.body)
            uid = data.get('uid', None)
            gid = data.get('gid', None)
            try:
                user_obj = User.objects.get(id=uid)
            except User.DoesNotExist:
                response['status'] = 1
                response['errmsg'] = '用户不存在'
                return JsonResponse(response)
            try:
                group_obj = Group.objects.get(id=gid)
            except Group.DoesNotExist:
                response['status'] = 1
                response['errmsg'] = '用户组不存在'
                return JsonResponse(response)
            user_obj.groups.add(group_obj)
            return JsonResponse(response)
        else:
            response['status'] = 1
            response['errmsg'] = '没有操作用户的权限'
            return JsonResponse(response)

class SearchUserView(LoginRequiredMixin, MyPermissionRequiredMixin, ListView):
    template_name = 'user/userlist.html'
    model = User
    paginate_by = 10
    before_range_num = 4
    after_range_num = 5
    ordering = 'id'

    permission_required = 'auth.view_user'

    def get_queryset(self):
        queryset = super(SearchUserView, self).get_queryset()
        queryset = queryset.filter(is_superuser=False)
        #查询条件
        username = self.request.GET.get('username', None)
        if username:
            queryset = queryset.filter(username__contains=username)
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
        context = super(SearchUserView, self).get_context_data(**kwargs)
        context['page_range_obj'] = self.get_page_range(context['page_obj'])

        #处理查询条件
        search_data = self.request.GET.copy()
        try:
            search_data.pop("page")
        except:
            GetLogger().get_logger().error(traceback.format_exc())
            pass
        context.update(search_data.dict())
        context['search_data'] = "&" + search_data.urlencode()
        return context

class GetUserListView(View):
    def get(self, request):
        user = User.objects.values("id", "email", "username")
        return JsonResponse(list(user), safe=False)