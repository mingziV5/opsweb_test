from django import forms
from django.contrib.auth.models import ContentType

class CreatePermissionForm(forms.Form):
    content_type = forms.IntegerField(required=True)
    codename = forms.CharField(required=True)
    name = forms.CharField(required=True)

    def clean_codename(self):
        codename = self.cleaned_data.get('codename')
        if codename.find(' ')>=0:
            raise forms.ValidationError('codename 不能有空格')
        return codename

    def clean_content_type(self):
        content_type_id = self.cleaned_data.get('content_type')
        try:
            content_type = ContentType.objects.get(pk=content_type_id)
            return content_type
        except Exception as e:
            raise forms.ValidationError('模型不存在')
