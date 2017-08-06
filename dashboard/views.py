from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
# login_required 默认会跳转到/accounts/login/ 可以在settings文件中修改LOGIN_URL来修改，后面还会加上你请求的url作为next的参数，做登陆跳转
# Create your views here.

'''
def index(request):
    print(request)
    print(request.scheme)
    print(request.path)
    print(request.method)
    print(request.encoding)
    print(request.META)
    print(request.get_host())
    print(request.get_port())
    print(request.get_full_path())
    print(request.is_secure())
    print(request.is_ajax())
    return HttpResponse('Hello World !!!')
def index(request):
    ret = {'name': 'reboot'}
    ret_list = ['json', 'python', 'golang', 'reboot']
    t = loader.get_template('text.html')
    context = {'name': 'parameter name'}
    return JsonResponse(ret_list, safe=False)
def index(request):
    print(request.GET)
    t = loader.get_template('test.html')
    context = {'name': 'parameter name'}
    #return HttpResponse(t.render(context, request))
    #省略HttpResponse,用render作封装
    return render(request, 'test.html', context)
def index(request):
    context = {'name': 'parameter aaaa'}
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        if username == 'aaaa' and password == 'aaaa':
            return HttpResponse('登陆成功')
        else:
            return HttpResponse('登陆失败')
    return render(request, 'test.html', context)
'''
@login_required
def index(request):
    return render(request, 'index.html')
