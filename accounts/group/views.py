from django.views.generic import ListView,View,TemplateView
from django.contrib.auth.models import Group, User, Permission, ContentType
from django.http import JsonResponse
from django.db import IntegrityError
from django.http import QueryDict
from django.shortcuts import redirect
import traceback

from django.contrib.auth.mixins import LoginRequiredMixin
from permissions.mixins import MyPermissionRequiredMixin

class GroupListView(LoginRequiredMixin, MyPermissionRequiredMixin, ListView):
    template_name = "group/grouplist.html"
    model = Group
    #指定权限
    permission_required = "auth.add_group"
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
            response['group_id'] = group.id
            response['group_name'] = group.name
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
            #查询用户组内成员
            #1
            group_obj = Group.objects.get(id=gid)
            members = group_obj.user_set.all()
            #2
            #User.objects.all().filter(用户组=组id)
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
            #通过组删除用户
            #group_obj.user_set.remove(user_obj)
            return JsonResponse(response)

        except:
            print(traceback.format_exc())
            response['status'] = 1
            response['errmsg'] = '删除组成员错误'
            return JsonResponse(response)

class GroupPermissionList(TemplateView):
    template_name = "group/modify_group_permissions.html"

    def get_context_data(self, **kwargs):
        context = super(GroupPermissionList, self).get_context_data(**kwargs)
        context["contenttypes"] = ContentType.objects.all()
        context["group"] = self.request.GET.get("gid", None)
        context["group_permissions"] = self.get_group_permissions(context["group"])
        print(context)
        return context

    def get_group_permissions(self, groupid):
        try:
            group_obj = Group.objects.get(pk=groupid)
            return [p.id for p in group_obj.permissions.all()]
        except Group.DoesNotExist:
            return redirect("error", next="group_list", msg="用户组不存在")

    def post(self, request):
        permission_id_list = request.POST.getlist("permission", [])
        groupid = request.POST.get("groupid", None)
        print(groupid)
        try:
            group_obj = Group.objects.get(pk=groupid)
        except Group.DoesNotExist:
            return redirect("error", next="group_list", msg="用户组不存在")
        if len(permission_id_list) > 0:
            permission_objs = Permission.objects.filter(id__in=permission_id_list)
            group_obj.permissions.set(permission_objs)
        else:
            group_obj.permissions.clear()
        return redirect("success", next="group_list")


