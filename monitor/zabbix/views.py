from django.views.generic import View,TemplateView
from django.http import JsonResponse, QueryDict
from opsweb.utils import GetLogger
from monitor.zabbix.client import cache_host, Zabbix, create_host, unlink_template, link_template
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
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace', 'search']

    def get_context_data(self, **kwargs):
        context = super(HostRsyncView, self).get_context_data(**kwargs)
        context['groups'] = Zabbix().get_groups()
        context['templates'] = Zabbix().get_templates()
        context['ztree'] = Ztree().get(async=True)
        return context

    def _change_to_dict(self, my_list, my_key):
        new_list = []
        for i in my_list:
            my_dict = {}
            my_dict.setdefault(my_key, i)
            new_list.append(my_dict)
        return new_list

    def post(self, request):
        ret = {'status': 0}
        groups = request.POST.getlist("group", [])
        server = request.POST.getlist("server", [])
        templates = request.POST.getlist('template', [])
        templates = Zabbix().filter_templates(templates)
        groups = self._change_to_dict(groups, 'groupid')
        templates = self._change_to_dict(templates, 'templateid')

        ret_data = create_host(server, groups, templates)
        ret["data"] = ret_data
        return JsonResponse(ret)

    def search(self, request):
        response = {}
        data = QueryDict(request.body)
        key_value = data.get('key', None)
        if not key_value:
            GetLogger().get_logger().error('搜索主机key_value为空')
        try:
            servers = Server.objects.filter(hostname__icontains=key_value).values('id', 'hostname')
        except Exception as e:
            GetLogger().get_logger().error('发生异常： {}'.format(e))
        servers = list(servers)
        return JsonResponse(servers, safe=False)


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

class LinkTemplateView(TemplateView):
    template_name = 'zabbix/link_template.html'

    def get_context_data(self, **kwargs):
        context = super(LinkTemplateView, self).get_context_data(**kwargs)
        context['ztree'] = Ztree().get()
        context['templates'] = Zabbix().get_templates()
        return context

    def delete(self, request):
        ret = {'status': 0}
        params = QueryDict(request.body)
        hostid = params.get('hostid', None)
        templateid = params.get('templateid', None)

        if not hostid:
            ret['status'] = 1
            ret['errmsg'] = '参数错误， 没有指定主机'
            return JsonResponse(ret)
        if not templateid:
            ret['status'] = 1
            ret['errmsg'] = '参数错误，没有指定模板'
            return JsonResponse(ret)
        try:
            unlink_template(hostid, templateid)
        except Exception as e:
            ret['status'] = 1
            ret['errmsg'] = e.args
        return JsonResponse(ret)

    def post(self, request):
        ret = {'status': 0}
        hostids = request.POST.getlist('hostids[]', [])
        templateids = request.POST.getlist('templateids[]', [])
        if not hostids:
            ret['status'] = 1
            ret['errmsg'] = '参数错误，没有指定主机'
            return JsonResponse(ret)
        if not templateids:
            ret['status'] = 1
            ret['errmsg'] = '参数错误， 没有指定模板'
            return JsonResponse(ret)
        ret['data'] = link_template(hostids, templateids)
        return JsonResponse(ret)

class GetHostTemplatesView(View):
    def get(self, request):
        ret = []
        servers = Server.objects.filter(server_purpose=request.GET.get('id', None))
        GetLogger().get_logger().info('服务器列表长度: {}'.format(len(servers)))
        for server in servers:
            data = {}
            data['hostname'] = server.hostname
            data['id'] = server.id

            if hasattr(server, 'zabbixhost'):
                GetLogger().get_logger().info('{}有监控'.format(server.hostname))
                data['monitor'] = True
                templates = Zabbix().get_templates(hostids=server.zabbixhost.hostid)
                if templates:
                    data['templates_flag'] = True
                    data['templates'] = templates
                else:
                    data['templates_flag'] = False
            else:
                GetLogger().get_logger().info('{}没有监控'.format(server.hostname))
                data['monitor'] = False
            ret.append(data)
        return JsonResponse(ret, safe=False)