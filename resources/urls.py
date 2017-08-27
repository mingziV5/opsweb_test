from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^idc/', include([
        url(r'^add/$', views.CreateIdcView.as_view(), name='idc_add')
    ]))
]