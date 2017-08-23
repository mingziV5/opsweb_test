from django.conf.urls import include, url
from . import views, user, group

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
    url(r'user/list/', user.views.UserListView.as_view(), name='user_list'),
    #list类视图
    #url(r'user/list/', views.LUserListView.as_view(), name='user_list'),
    #url(r'user/list/', user.UserListView.as_view(), name='user_list'),
    url(r'^user/', include([
        url(r'^modify/', include([
            url(r'^status/$', user.views.ModifyUserStatusView.as_view(), name='user_modify_status'),
            url(r'^group/$', user.views.ModifyUserGroupView.as_view(), name='user_modify_group'),
        ]))
    ])),

    url(r'^group/', include([
        url(r'^$', group.views.GroupListView.as_view(), name='group_list'),
        url(r'^create/$', group.views.ModifyGroupView.as_view(), name='group_create'),
        url(r'^del/$', group.views.ModifyGroupView.as_view(), name='group_del'),
        url(r'^member/', include([
            url(r'^get/$', group.views.GroupMemberListView.as_view(), name='group_members'),
            url(r'^del/$', group.views.GroupMemberListView.as_view(), name='group_members_del'),
        ]))
    ])),
]
