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

'''
TemplateView Method Not Allowed (POST)
class UserLoginTplView(TemplateView):
    template_name = 'public/login.html'

    def get_context_data(self, **kwargs):
        context = super(UserLoginTplView, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            username = self.request.POST.get('username', None)
            password = self.request.POST.get('password', None)
            user = authenticate(username = username, password = password)
            if user:
                login(self.request, user)
                context['status'] = 0
                context['next_url'] = self.request.GET.get('next') if self.request.GET.get('next', None) else '/'
            else:
                context['status'] = 1
                context['errmsg'] = '用户名密码错误'
            return context
        else:
            return context
'''