from django.views.generic import View,TemplateView
from django.http import JsonResponse
from opsweb.utils import GetLogger
from monitor.zabbix.client import cache_host, Zabbix, create_host
from resources.product.view import Ztree
from resources.server.models import Server

class ZabbixCacheHostView(View):
    def get(self, request):
        ret = {'status': 0}
        try:
            cache_host()
        except Exception as e:
            GetLogger().get_logger().error('zabbix 同步失败')
        GetLogger().get_logger().info('zabbix 同步成功')
        return JsonResponse(ret)

class HostRsyncView(TemplateView):
    template_name = 'zabbix/host_rsync.html'

    def get_context_data(self, **kwargs):
        context = super(HostRsyncView, self).get_context_data(**kwargs)
        context['groups'] = Zabbix().get_groups()
        context['ztree'] = Ztree().get(async=True)
        return context

    def post(self, request):
        ret = {'status': 0}
        group = request.POST.get("group", "")
        server = request.POST.getlist("server", [])
        ret_data = create_host(server, group)
        ret["data"] = ret_data
        return JsonResponse(ret)

class AsyncView(View):

    def get(self, request):
        server_purpose = request.GET.get('id', None)
        ret = []
        for s in Server.objects.filter(server_purpose=server_purpose):
            z_data = {}
            z_data['id'] = s.id
            z_data['name'] = s.hostname
            ret.append(z_data)
        return JsonResponse(ret, safe=False)