from django.conf.urls import include, url
from resources.idc import views

urlpatterns = [
    url(r'^idc/', include([
        url(r'^add/$', views.CreateIdcView.as_view(), name='idc_add'),
        url(r'^list/$', views.IdcListView.as_view(), name='idc_list'),
        url(r'^Modify/$', views.ModifyIdcView.as_view(), name="modify_idc"),
    ]))
]