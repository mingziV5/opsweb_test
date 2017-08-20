from django.views.generic import View, TemplateView
from django.contrib.auth import authenticate, login, logout
from django.http.response import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.http import QueryDict
from django.urls import reverse
from django.contrib.auth.models import User, Group

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

class ModifyUserStatusView(View):
    def post(self, request):
        uid = request.POST.get('uid', None)
        print(uid)
        response = {}
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

class ModifyUserGroupView(View):
    def get(self, request):
        uid = request.GET.get('uid', None)
        group_objs = Group.objects.all()
        try:
            user_obj = User.objects.get(id=uid)
        except User.DoesNotExist:
            pass
        else:
            group_objs = group_objs.exclude(id__in=user_obj.groups.values_list('id'))
        return JsonResponse(list(group_objs.values('id', 'name')), safe=False)

    def put(self, request):
        response = {'status': 0}
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
