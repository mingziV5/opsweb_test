from django.views.generic import TemplateView
from django.shortcuts import redirect, reverse
from django.http import JsonResponse
from resources.models import Idc

import traceback
# Create your views here.

#通过页面submit提交
class CreateIdcView(TemplateView):
    template_name = "idc/add_idc.html"

    def post(self, request):
        #print(request.POST)
        #print(reverse("success", kwargs={"next": "user_list"}))
        add_idc_form = request.POST.copy()
        add_idc_form.pop('csrfmiddlewaretoken')
        add_idc_dict = add_idc_form.dict()
        try:
            idc = Idc(**add_idc_dict)
            idc.save()
            return redirect("success", next="user_list")
        except:
            print(traceback.format_exc())
            errmsg = '添加idc信息错误'
            return redirect("error", next="idc_add", msg=errmsg)
        #操作成功

        #操作失败
        #return redirect("error", next="idc_add", msg="error")
        #return HttpResponse("")

#TODO
#通过ajax提交