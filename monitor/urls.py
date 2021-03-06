from django.conf.urls import include, url
from . import zabbix
from . import influx

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
    url(r'^influx/', include([
        url(r'^get/$', influx.views.InfluxApiView.as_view(), name='influx_api'),
        url(r'^graph/', include([
            url(r'^modify/$', influx.views.GraphProductModifyView.as_view(), name='influx_graph_product_modify'),
            url(r'^test/$', influx.views.TestGrapView.as_view(), name='influx_graph_test'),
            url(r'^update/$', influx.views.GraphModifyView.as_view(), name='influx_graph_modify'),
            url(r'^product/$', influx.views.ProductGraphView.as_view(), name='influx_product_graph'),
            url(r'^create/$', influx.views.CreateGrapView.as_view(), name='influx_graph_create'),
            url(r'^list/$', influx.views.GraphListView.as_view(), name='influx_graph_list'),
            url(r'^manager/$', influx.views.ManagerGraphView.as_view(), name='influx_grap_manager'),
            url(r"^detail/$", influx.views.GraphGetView.as_view(), name="influx_graph_detail"),
        ])),
    ]))
]