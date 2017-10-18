from django import forms
from resources.product.models import Product
from django.contrib.auth.models import User

class AddProductForm(forms.Form):
    service_name = forms.CharField(required=True)
    module_letter = forms.CharField(required=True)
    op_interface = forms.MultipleChoiceField(choices=((u.email, u.username) for u in User.objects.filter(is_superuser=False)))
    dev_interface = forms.MultipleChoiceField(choices=((u.email, u.username) for u in User.objects.filter(is_superuser=False)))
    pid = forms.IntegerField(required=True)

    def clean_pid(self):
        pid = self.cleaned_data.get('pid')
        if int(pid) != 0:
            try:
                p_obj = Product.objects.get(pk=pid)
                if p_obj.pid !=0:
                    raise forms.ValidationError("请选择正确的一级业务线")
            except Product.DoesNotExist:
                raise forms.ValidationError("请选择正确的一级业务线")
        return pid

    def clean_dev_interface(self):
        dev_interface = self.cleaned_data['dev_interface']
        return ','.join(dev_interface)

    def clean_op_interface(self):
        op_interface = self.cleaned_data['op_interface']
        return ','.join(op_interface)

class ModifyProductForm(forms.Form):
    id = forms.IntegerField(required=True)
    service_name = forms.CharField(required=True)
    module_letter = forms.CharField(required=True)
    op_interface = forms.CharField(required=True)
    dev_interface = forms.CharField(required=True)
    #op_interface = forms.MultipleChoiceField(choices=((u.email, u.username) for u in User.objects.filter(is_superuser=False)))
    #dev_interface = forms.MultipleChoiceField(choices=((u.email, u.username) for u in User.objects.filter(is_superuser=False)))

    '''
    def clean_dev_interface(self):
        dev_interface = self.cleaned_data['dev_interface']
        return ','.join(dev_interface)

    def clean_op_interface(self):
        op_interface = self.cleaned_data['op_interface']
        return ','.join(op_interface)
    '''