from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^login/$', views.user_login, name='user_login'),
    url(r'^logout/$', views.user_logout, name='user_logout'),
    #url(r'user/list/$', views.user_list_view, name='user_list'),
    #类视图，as_view()方法
    #url(r'user/list/$', views.UserListView.as_view(), name='user_list'),
    #模板类视图
    #url(r'user/list/', views.TplUserListView.as_view(), name='user_list'),
    #list类视图
    #url(r'user/list/', views.LUserListView.as_view(), name='user_list'),
    url(r'user/list/', accounts.UserListView.as_view(), name='user_list'),
]
