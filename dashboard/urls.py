from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^urlpos/([0-9]{4})/([0-9]{2})/([0-9]{2})/$', views.key_world_test, name='position'),
    url(r'^urlkey/(?P<year>[0-9]{4})/(?P<month>[0-9]{2}/(?P<day>[0-9]{2})/$)', views.key_world_test, name='key_world'),
    url(r'^success/(?P<next>[\s\S]*)/$', views.SuccessView.as_view(), name='success'),
    url(r'^error/(?P<next>[\s\S]*)/(?P<msg>[\s\S\\u4e00-\\u9fa5]*)/$', views.ErrorView.as_view(), name="error"),
]
