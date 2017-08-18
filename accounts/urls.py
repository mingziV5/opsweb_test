from django.conf.urls import include, url
from . import views, user

urlpatterns = [
    #views
    #url(r'^login/$', views.user_login, name='user_login'),
    #url(r'^logout/$', views.user_logout, name='user_logout'),
    #view类视图
    #url(r'^login/$', user.views.UserLoginView.as_view(), name='user_login'),
    #url(r'^logout/$', user.views.UserLogoutView.as_view(), name='user_logout'),
    #template类视图
    url(r'^login/$', user.views.UserLoginTplView.as_view(), name='user_login'),
    url(r'^logout/$', user.views.UserlogoutTplView.as_view(), name='user_logout'),
    #url(r'user/list/$', views.user_list_view, name='user_list'),
    #类视图，as_view()方法
    #url(r'user/list/$', views.UserListView.as_view(), name='user_list'),
    #模板类视图
    url(r'user/list/', views.TplUserListView.as_view(), name='user_list'),
    #list类视图
    #url(r'user/list/', views.LUserListView.as_view(), name='user_list'),
    #url(r'user/list/', user.UserListView.as_view(), name='user_list'),
]
