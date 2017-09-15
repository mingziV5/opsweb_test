from django.conf.urls import include, url
from permissions import views

urlpatterns = [
    url(r'^list/$', views.PermissionListView.as_view(), name="permission_list"),
    url(r'^add/$', views.PermissionAddView.as_view(), name="permission_add"),
    url(r'^t_add/$', views.PermissionAddTplView.as_view(), name="permission_add_t")
]