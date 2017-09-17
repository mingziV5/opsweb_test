from django.conf.urls import include, url
from resources import idc
from resources import server
from resources import product
urlpatterns = [
    url(r'^idc/', include([
        url(r'^add/$', idc.views.CreateIdcView.as_view(), name='idc_add'),
        url(r'^list/$', idc.views.IdcListView.as_view(), name='idc_list'),
        url(r'^Modify/$', idc.views.ModifyIdcView.as_view(), name="modify_idc"),
    ])),
    url(r'^server/', include([
        url(r'report/$', server.view.ServerInfoAutoReport, name="server_report"),
        url(r'list/$', server.view.ServerListView.as_view(), name="server_list")
    ])),
    url(r'^product/', include([
        url(r'add/$', product.view.AddProductView.as_view(), name="product_add")
    ]))
]