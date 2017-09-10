from django import forms
from resources.idc.models import Idc

class CreateIdcForm(forms.Form):
    name = forms.CharField(required=True)
    full_name = forms.CharField(required=True)
    address = forms.CharField(required=True)
    phone = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    contact = forms.CharField(required=True)

    #自定义字段验证
    def clean_name(self):
        name = self.cleaned_data.get('name')
        try:
            Idc.objects.get(name__exact=name)
            raise forms.ValidationError('idc 名字已存在')
        except Idc.DoesNotExist:
            return name
    #表单级别验证，可以添加数据
    def clean(self):
        data = self.cleaned_data
        return data
