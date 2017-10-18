from django.views.generic import View, TemplateView
from django.http import JsonResponse
from django.contrib.auth.models import User
from resources.product.models import Product
from resources.idc.models import Idc
from resources import product
from resources.product.form import AddProductForm, ModifyProductForm
from django.shortcuts import redirect
import json
import traceback
from opsweb.utils import GetLogger

class AddProductView(TemplateView):
    template_name = 'product/add_product.html'

    def get_context_data(self, **kwargs):
        context = super(AddProductView, self).get_context_data(**kwargs)
        context['products'] = Product.objects.filter(pid__exact=0)
        context['userlist'] = User.objects.all()
        return context

    def post(self, request):
        product_form = AddProductForm(request.POST)
        print(request.body)
        if product_form.is_valid():
            product = Product(**product_form.cleaned_data)
            try:
                product.save()
                return redirect("success", next="product_manage")
            except Exception as e:
                GetLogger().get_logger().error(traceback.format_ext())
                return redirect("error", next="product_manage", msg=e.args)
        else:
            return redirect("error", next="product_manage",
                            msg=json.dumps(json.loads(product_form.errors.as_json()), ensure_ascii=False))

class ZnodeView(View):
    def get(self, request):
        ztree = Ztree()
        znode = ztree.get()
        return JsonResponse(znode, safe=False)

class Ztree(object):
    def __init__(self):
        self.data = self.get_product()

    def get_product(self):
        return Product.objects.all()

    def get(self, idc=False, async=False):
        ret = []
        for product in self.data.filter(pid=0):
            node = self.process_node(product)
            node["children"] = self.get_children(product.id, async)
            node["isParent"] = 'true'
            ret.append(node)
        if idc:
            return self.get_idc_node(ret)
        return ret

    def get_children(self, id, async=False):
        ret = []
        for product in self.data.filter(pid=id):
            node = self.process_node(product, async)
            ret.append(node)
        return ret

    def process_node(self, product_obj, async=False):
        ret =  {
            "name": product_obj.service_name,
            "id": product_obj.id,
            "pid": product_obj.pid
        }
        if async:
            ret['isParent'] = 'true'
        return ret

    def get_idc_node(self, nodes):
        ret = []
        for idc in Idc.objects.all():
            node = {
                "name": idc.full_name,
                "children": nodes,
                "isParent": 'true'
            }
            ret.append(node)
        return ret

class ProductGetView(View):
    def get(self, request):
        ret = {'status': 0}
        #三种情况 id , pid , 没有值
        p_id = self.request.GET.get('id', None)
        p_pid = self.request.GET.get('pid', None)
        if p_id:
            ret["data"] = self.get_obj_dict(p_id)
            return JsonResponse(ret)
        if p_pid:
            ret['data'] = self.get_products(p_pid)
            return JsonResponse(ret)
        return JsonResponse({})

    def get_obj_dict(self, p_id):
        try:
            product_obj = Product.objects.get(pk=p_id)
            ret = product_obj.__dict__
            ret.pop("_state")
            return ret
        except:
            return {}

    def get_products(self, pid):
        return list(Product.objects.filter(pid=pid).values())

class ProductManageView(TemplateView):
    template_name = "product/product_manage.html"

    def get_context_data(self, **kwargs):
        context = super(ProductManageView, self).get_context_data(**kwargs)
        context['ztree'] = Ztree().get()
        return context

    def post(self, request):
        response = {}
        product_form = ModifyProductForm(request.POST)
        print(request.body)
        if product_form.is_valid():
            try:
                pid = product_form.cleaned_data.get('id')
                print(product_form.cleaned_data)
                product_obj = Product.objects.get(pk=pid)
                product_obj.service_name = product_form.cleaned_data.get('service_name')
                product_obj.module_letter = product_form.cleaned_data.get('module_letter')
                product_obj.dev_interface = product_form.cleaned_data.get('dev_interface')
                product_obj.op_interface = product_form.cleaned_data.get('op_interface')
                product_obj.save()
                response['status'] = 0
            except Exception as e:
                GetLogger().get_logger().error('修改业务线出错： {}'.format(e))
                response['status'] = 1
                response['errmsg'] = '修改业务线出错'
        else:
            GetLogger().get_logger().error('数据验证错误')
            response['status'] = 1
            response['errmsg'] = '数据验证错误'
        return JsonResponse(response)


