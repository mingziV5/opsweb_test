from django.conf import settings
from zabbix_client import ZabbixServerProxy
#from pyzabbix import ZabbixAPI
from resources.server.models import Server
from monitor.zabbix.models import ZabbixHost
import json
import traceback
from opsweb.utils import GetLogger

class Zabbix(object):
    def __init__(self):
        self.zb = ZabbixServerProxy(settings.ZABBIX_API)
        self.zb.user.login(user=settings.ZABBIX_USER, password=settings.ZABBIX_USERPASS)

    def get_hosts(self):
        return self.zb.host.get(output=['hostid', 'host'], selectInterfaces=['ip'])

    def get_groups(self):
        return self.zb.hostgroup.get(output=['groupid', 'name'])

    def get_templates(self):
        return self.zb.template.get(output=['templateid', 'name'])

    def get_parent_templates(self):
        return self.zb.template.get(output=['templateid', 'name'], selectParentTemplates=['templateid', 'name'])

    def create_host(self, params):
        return self.zb.host.create(**params)

    def filter_templates(self, template_list):
        parent_templates = self.get_parent_templates()
        for templateid in template_list:
            for template_dict in parent_templates:
                if not template_dict['parentTemplates']:
                    continue
                if templateid == template_dict['templateid']:
                    for p_template_dict in template_dict['parentTemplates']:
                        if p_template_dict['templateid'] in template_list:
                            template_list.remove(p_template_dict['templateid'])
        return template_list
        #for templateid in template_list:



def process_zb_hosts(zbhosts):
    ret = []
    ip_list = []
    #拿到的数据
    # {'hostid': '10254', 'host': 'zabbix', 'interfaces': [{'ip': '192.168.1.2'}]}
    #整理以后的数据
    # {'hostid': '10254', 'host': 'zabbix', 'ip': '192.168.1.1'}
    for host in zbhosts:
        try:
            ip = host['interfaces'][0]['ip']
        except:
            GetLogger().get_logger().error(traceback.format_exc())
        del host['interfaces']
        host['ip'] = ip
        ret.append(host)
        if ip in ip_list:
            GetLogger().get_logger().error('ip 重复')
        else:
            ip_list.append(ip)
    return ret

def cache_host():
    #取出所有zabbix里的host信息
    zbhosts = process_zb_hosts(Zabbix().get_hosts())
    for host in zbhosts:
        #host数据格式
        #{'hostid': '10254', 'host': 'zabbix', 'ip': '192.168.1.1'}
        try:
            server_obj = Server.objects.get(inner_ip=host['ip'])
        except Server.DoesNotExist:
            GetLogger().get_logger().error('zabbix ip cmdb not exist')
        except Server.MultipleObjectsReturned:
            GetLogger().get_logger().error('ip cmdb more then once')
        else:
            host['server'] = server_obj
            zh = ZabbixHost(**host)
            zh.save()

def create_host(serverids, group=[{'groupid': "2"}], template=[{'templateid': "10001"}]):
    ret_data = []
    if isinstance(serverids, list) and serverids:
        for server in Server.objects.filter(id__in=serverids):
            zb_data = {}
            zb_data['hostname'] = server.hostname
            try:
                hostid = _create_host(server.hostname, server.inner_ip, group, template)
                zb_data['status'] = True
            except Exception as e:
                zb_data['status'] = False
                zb_data['errmsg'] = e.args
            else:
                try:
                    zb = ZabbixHost()
                    zb.server = server
                    zb.hostid = hostid
                    zb.ip = server.inner_ip
                    zb.host = server.hostname
                    zb.save()
                except Exception as e:
                    zb_data['status'] = False
                    zb_data['errmsg'] = "同步成功，缓存是失败"
            ret_data.append(zb_data)
    else:
        zb_data = {}
        zb_data['status'] = False
        zb_data['errmsg'] = '服务器组选择有误'
        ret_data.append(zb_data)
    return ret_data

def _create_host(hostname, ip, group, template, port="10050"):
    params = {

        'host': hostname,
        'interfaces': [
            {
                'dns': '',
                'ip': ip,
                'main': 1,
                'port': port,
                'type': 1,
                'useip': 1
             }
        ],
        'groups': group,
        'templates': template
    }
    #print(params)
    try:
        ret = Zabbix().create_host(params)
        GetLogger().get_logger().info("创建zabbix host 完成：{}".format(json.dumps(ret)))
        if "hostids" in ret:
            return ret["hostids"][0]
        else:
            raise Exception(ret["hostids"][0])
    except Exception as e:
        raise Exception(e.args[0])