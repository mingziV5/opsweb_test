from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.views.generic import View, TemplateView, ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
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

'''
def user_list_view(request):
    user_queryset = User.objects.all()
    for user in user_queryset:
        print (user.username, user.email)
    return render(request, 'user/userlist.html', {'userlist': user_queryset})
'''

class UserListView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user_queryset = User.objects.all()
        return render(request, 'user/userlist.html', {'userlist': user_queryset})

class TplUserListView(LoginRequiredMixin, TemplateView):
    template_name = 'user/userlist.html'
    counts = 10

    # def get_context_data_back(self, **kwargs):
    #     context = super(TplUserListView, self).get_context_data(**kwargs)
    #     users = User.objects.all()
    #     try:
    #         page = int(self.request.GET.get('page', 1))
    #     except:
    #         page = 1
    #     end = self.counts*page
    #     start = end - self.counts
    #     context['userlist'] = users[start:end]
    #     return context

    def get_context_data(self, **kwargs):
        context = super(TplUserListView, self).get_context_data(**kwargs)
        try:
            page = int(self.request.GET.get('page', 1))
        except:
            page = 1
        user_list = User.objects.all()
        paginator = Paginator(user_list, self.counts)
        if page < 8:
            start_page = 0
            end_page = page + 7
        elif page >= 8 and page <= paginator.num_pages - 8:
            start_page = page - 8
            end_page = page + 7
        elif page > paginator.num_pages -8:
            start_page = page - 8
            end_page = paginator.num_pages
        page_range_obj = paginator.page_range[start_page:end_page]
        context['page_obj'] = paginator.page(page)
        context['page_range_obj'] = page_range_obj
        print(context)
        return context

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', None)
        print(page)
        return super(TplUserListView, self).get(request, *args, **kwargs) 

class LUserListView(LoginRequiredMixin, ListView):
    template_name = 'user/userlist.html'
    model = User
    paginate_by = 8

class LoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('user_login'))
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
