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
        url(r'list/$', server.view.ServerListView.as_view(), name="server_list"),
        url(r'status/$', server.view.ModifyServerStatusView.as_view(), name="server_status_modify"),
        url(r'get/$', server.view.GetServerListView.as_view(), name="server_get"),
        url(r'modify/', include([
            url(r'product/$', server.view.ServerModifyProductView.as_view(), name="server_modify_product")
        ]))
    ])),
    url(r'^product/', include([
        url(r'add/$', product.view.AddProductView.as_view(), name="product_add"),
        url(r'ztreetest/$', product.view.ZnodeView.as_view(), name="product_ztree_test"),
        url(r'get/$', product.view.ProductGetView.as_view(), name="product_get"),
        url(r'manage/$', product.view.ProductManageView.as_view(), name="product_manage"),
    ]))
]