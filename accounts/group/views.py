from django.views.generic import ListView,View
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.db import IntegrityError

class GroupListView(ListView):
    template_name = "group/grouplist.html"
    model = Group

class GroupCreateView(View):

    def post(self, request):
        group_name = request.POST.get('name', None)
        response = {}
        if not group_name:
            response['status'] = 1
            response['errmsg'] = '不能为空'
            return JsonResponse(response)
        try:
            group = Group(name=group_name)
            group.save()
            response['status'] = 0
        except IntegrityError:
            response['status'] =1
            response['errmsg'] = '用户组以存在'
        except:
            response['status'] = 1
            response['errmsg'] = '添加用户组失败'
        return JsonResponse(response)