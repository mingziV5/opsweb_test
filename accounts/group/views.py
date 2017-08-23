from django.views.generic import ListView,View
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.db import IntegrityError
from django.http import QueryDict
import traceback

class GroupListView(ListView):
    template_name = "group/grouplist.html"
    model = Group

class ModifyGroupView(View):

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

    def delete(self, request):
        response = {'status': 0}
        data = QueryDict(request.body)
        gid = data.get('gid', None)
        if not gid:
            response['status'] = 1
            response['errmsg'] = 'gid不能为空'
            return JsonResponse(response)
        group_obj = Group.objects.get(id=gid)
        if group_obj.user_set.all().count() != 0:
            response['status'] = 1
            response['errmsg'] = '不能删除，组内还有成员'
            return JsonResponse(response)
        try:
            group_obj.delete()
            response['status'] == 0
            return JsonResponse(response)
        except:
            print(traceback.format_exc())
            response['status'] == 1
            response['errmsg'] == '删除组出错'
            return JsonResponse(response)


class GroupMemberListView(View):

    def get(self, request):
        gid = request.GET.get('gid', None)
        response = {}
        if not gid:
            response['status'] = 1
            response['errmsg'] = 'gid不能为空'
            return JsonResponse(response)
        try:
            group_obj = Group.objects.get(id=gid)
            members = group_obj.user_set.all()
            list_members = list(members.values('id', 'username'))
            response['status'] = 0
            response['list_members'] = list_members
            return JsonResponse(response)
        except:
            print(traceback.format_exc())
            response['status'] = 1
            response['errmsg'] = '查找组成员错误'
            return JsonResponse(response)

    def delete(self, request):
        response = {'status': 0}
        data = QueryDict(request.body)
        uid = data.get('uid', None)
        gid = data.get('gid', None)

        if not uid or not gid:
            response['status'] = 1
            response['errmsg'] = 'gid 或者 uid 为空'
            return JsonResponse(response)

        try:
            user_obj = User.objects.get(id=uid)
            group_obj = Group.objects.get(id=gid)
            user_obj.groups.remove(group_obj)
            return JsonResponse(response)

        except:
            print(traceback.format_exc())
            response['status'] = 1
            response['errmsg'] = '删除组成员错误'
            return JsonResponse(response)




