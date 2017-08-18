from django.views.generic import View, TemplateView
from django.contrib.auth import authenticate, login, logout
from django.http.response import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

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