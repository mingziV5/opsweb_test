from django.views.generic import View, TemplateView
from django.contrib.auth.models import User
from resources.models import Product
from resources.product.form import AddProductForm
from django.shortcuts import redirect
import json
import traceback

class AddProductView(TemplateView):
    template_name = 'product/add_product.html'

    def get_context_data(self, **kwargs):
        context = super(AddProductView, self).get_context_data(**kwargs)
        context['products'] = Product.objects.filter(pid__exact=0)
        context['userlist'] = User.objects.all()
        return context

    def post(self, request):
        product_form = AddProductForm(request.POST)
        if product_form.is_valid():
            product = Product(**product_form.cleaned_data)
            try:
                product.save()
                return redirect("success", next="idc_list")
            except Exception as e:
                print(traceback.format_exc())
                return redirect("error", next="idc_list", msg=e.args)
        else:
            return redirect("error", next="idc_list",
                            msg=json.dumps(json.loads(product_form.errors.as_json()), ensure_ascii=False))