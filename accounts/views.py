from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
# Create your views here.
def user_login(request):
    if request.method == 'GET':
        return render(request, "public/login.html")
    else:
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        #用户名和密码正确且user.is_active == True
        user = authenticate(username=username, password=password)
        response = {'status':0, 'errmsg': ''}
        if user:
            #用户可以登陆
            login(request, user)
            response['next_url'] = request.GET.get('next') if request.GET.get('next', None) else '/'
        else:
            response['status'] = 1
            response['errmsg'] = '用户名密码错误'
        return JsonResponse(response)

def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("user_login"))
