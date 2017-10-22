from django.conf.urls import include, url
from . import zabbix

urlpatterns = [
    url(r'^zabbix/', include([
        url(r'^cachehost/$', zabbix.views.ZabbixCacheHostView.as_view(), name='zabbix_get'),
        url(r'^host/', include([
            url(r'^rsync/$', zabbix.views.HostRsyncView.as_view(), name="zabbix_host_rsync"),
            url(r'^async/$', zabbix.views.AsyncView.as_view(), name="zabbix_host_async"),  # 异步加载数据
            url(r'^linktemplate/$', zabbix.views.LinkTemplateView.as_view(), name='zabbix_host_linktemplate'),
            url(r'^gettemplate/$', zabbix.views.GetHostTemplatesView.as_view(), name='zabbix_host_templates'),
        ])),
    ])),
]