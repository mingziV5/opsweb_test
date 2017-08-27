from django.views.generic import TemplateView
from django.shortcuts import redirect, reverse
from django.http import HttpResponse
# Create your views here.

class CreateIdcView(TemplateView):
    template_name = "idc/add_idc.html"

    def post(self, request):
        print(request.POST)
        print(reverse("success", kwargs={"next": "user_list"}))
        #操作成功
        return redirect("success", next="user_list")
        #操作失败
        #return redirect("error", next="idc_add", msg="error")
        #return HttpResponse("")