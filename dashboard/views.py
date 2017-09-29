from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.urls import reverse
from django.utils.http import unquote_plus
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


def key_world_test(request, *args, **kwargs):
    print (args)
    print (kwargs)
    return HttpResponse('OK')
    
class IndexView(TemplateView):
    template_name = 'index.html'

class SuccessView(TemplateView):
    template_name = "public/success.html"

    def get_context_data(self, **kwargs):
        context = super(SuccessView, self).get_context_data(**kwargs)
        success_name = self.kwargs.get("next", "")

        try:
            next_url = reverse(success_name)
        except:
            next_url = unquote_plus(success_name)
        context['next_url'] = next_url
        return context

class ErrorView(TemplateView):
    template_name = "public/error.html"

    def get_context_data(self, **kwargs):
        context = super(ErrorView, self).get_context_data(**kwargs)
        error_name = self.kwargs.get("next", "")
        errmsg = self.kwargs.get('msg', "")
        try:
            next_url = reverse(error_name)
        except:
            next_url = unquote_plus(error_name)
        context['next_url'] = next_url
        context['errmsg'] = errmsg
        return context



