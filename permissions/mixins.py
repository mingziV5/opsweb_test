from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.http.response import JsonResponse

class MyPermissionRequiredMixin(PermissionRequiredMixin):

    next_url = 'index'

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return redirect('error', next=self.next_url, msg='没有权限')
        return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)


def my_permission_required(permission, request):

    user = request.user

    if user.has_perm(permission):
        return True
    else:
        response = {'response': 1, 'errmsg': '没有相应的权限'}
        return JsonResponse(response)
