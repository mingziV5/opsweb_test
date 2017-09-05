from django.views.generic import TemplateView, ListView, View
from django.shortcuts import redirect, reverse
from django.http import JsonResponse
from resources.idc.models import Idc
from django.http import QueryDict
from django.contrib.auth.mixins import LoginRequiredMixin
import traceback
# Create your views here.

#通过页面submit提交
class CreateIdcView(LoginRequiredMixin, TemplateView):
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
            return redirect("success", next="idc_list")
        except:
            print(traceback.format_exc())
            errmsg = '添加idc信息错误'
            return redirect("error", next="idc_add", msg=errmsg)
        #操作成功
        #操作失败
        #return redirect("error", next="idc_add", msg="error")
        #return HttpResponse("")

    """
    通过ajax提交表单信息
    def post(self, request):
        add_idc_form = request.POST.copy()
        add_idc_form.pop('csrfmiddlewaretoken')
        add_idc_dict = add_idc_form.dict()
        response = {}
        try:
            idc = Idc(**add_idc_dict)
            idc.save()
            response['status'] = 0
            response['next_url'] = 'idc_list'
            return JsonResponse(response)
        except:
            print(traceback.format_exc())
            response['status'] = 1
            response['errmsg'] = '添加idc信息错误'
            return JsonResponse(response)
    """
    """
    作业
    def post(self, request):
        name = request.POST.get('name', None)
        full_name = request.POST.get('full_name', None)
        address = request.POST.get('address', None)
        username = request.POST.get('username', None)
        phone = request.POST.get('phone', None)
        email = request.POST.get('email', None)
        #验证数据
        errmsg = []
        if not name:
            errmsg.append("idc name is null")
        if not full_name:
            errmsg.append("idc full name is null")
        if errmsg:
            return redirect("error", next="idc_add", msg=json.dumps(errmsg))

        idc = Idc()
        idc.name = name
        idc.full_name = full_name
        idc.address = address
        idc.username = username
        idc.phone = phone
        idc.email = email

        try:
            idc.save()
            return redirect("success", next="idc_list")
        except Exception as e:
            return redirect("error", next="idc_add", msg=e.args)
        return redirect("success", next="idc_list")
        """

class IdcListView(LoginRequiredMixin, ListView):
    template_name = "idc/idc_list.html"
    model = Idc
    paginate_by = 10
    before_range_num = 4
    after_range_num = 5
    ordering = 'id'

    def get_queryset(self):
        queryset = super(IdcListView, self).get_queryset()
        queryset = queryset.values('id','name','full_name','contact','phone')
        return queryset

    def get_page_range(self, page_obj):
        current_index = page_obj.number
        start = current_index - self.before_range_num
        end = current_index + self.after_range_num
        if start <= 0:
            start = 1
        if end > page_obj.paginator.num_pages:
            end = page_obj.paginator.num_pages
        return range(start, end+1)

    def get_context_data(self, **kwargs):
        context = super(IdcListView, self).get_context_data(**kwargs)
        context['page_range_obj'] = self.get_page_range(context['page_obj'])
        print(context)
        return context

class ModifyIdcView(LoginRequiredMixin, View):

    def post(self, request):
        add_idc_form = request.POST.copy()
        add_idc_form.pop('csrfmiddlewaretoken')
        add_idc_dict = add_idc_form.dict()
        response = {}
        try:
            idc = Idc(**add_idc_dict)
            idc.save()
            response['status'] = 0
            response['next_url'] = 'idc_list'
            return JsonResponse(response)
        except:
            print(traceback.format_exc())
            response['status'] = 1
            response['errmsg'] = '添加idc信息错误'
            return JsonResponse(response)

    def get(self, request):
        idc_id = request.GET.get('id', None)
        response = {}
        if not idc_id:
            response['status'] = 1
            response['errmsg'] = 'idc ID 为空'
            return JsonResponse(response)
        try:
            idc = Idc.objects.filter(id=idc_id).values('id','name', 'full_name', 'address', 'phone', 'email', 'contact')
            response['status'] = 0
            response['idc_obj'] = list(idc)[0]
            print(response)
            return JsonResponse(response)
        except:
            print(traceback.format_exc())
            response['status'] = 1
            response['errmsg'] = '查询出错'
            return JsonResponse(response)

    def put(self,request):
        data = QueryDict(request.body)
        idc_id = data.get('id', None)
        name = data.get('name', None)
        full_name = data.get('full_name', None)
        address = data.get('address', None)
        phone = data.get('phone', None)
        email = data.get('email', None)
        contact = data.get('contact', None)
        response = {}
        try:
            idc = Idc.objects.get(id=idc_id)
            idc.name = name
            idc.full_name = full_name
            idc.address = address
            idc.phone = phone
            idc.email = email
            idc.contact = contact
            idc.save()
            response['status'] = 0
        except:
            print(traceback.format_exc())
            response['status'] = 1
            response['errmsg'] = '更新idc出错'
        return JsonResponse(response)

    def delete(self, request):
        data = QueryDict(request.body)
        idc_id = data.get('idc_id', None)
        response = {}
        try:
            idc = Idc.objects.get(id=idc_id)
            idc.delete()
            response['status'] = 0
            return JsonResponse(response)
        except:
            print(traceback.fomat_exc())
            response['status'] = 1
            response['errmsg'] = '删除idc出错'

