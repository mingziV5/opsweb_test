from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect

class MyPermissionRequiredMixin(PermissionRequiredMixin):

    next_url = 'index'

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return redirect('error', next=self.next_url, msg='没有权限')
        return super(PermissionRequiredMixin, self).dispatch(request, *args, **kwargs)