from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^login/$', views.user_login, name='user_login'),
    url(r'^logout/$', views.user_logout, name='user_logout'),
    url(r'user/list/$', views.user_logout, name='user_list'),
]
