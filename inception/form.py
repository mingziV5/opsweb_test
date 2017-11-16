from django import forms
from django.contrib.auth.models import User, Group

class AddSqlWorkflow(forms.Form):
    workflow_name = forms.CharField(required=True)
    reviewer = forms.MultipleChoiceField(choices=((u.email, u.username) for u in User.objects.filter(groups__name='dba')))
    backup = forms.CharField(required=True)
    cluster_db_name = forms.CharField(required=True)
    sql_content = forms.CharField(required=True)
    is_split = forms.CharField(required=True)

    def clean_reviewer(self):
        reviewer = self.cleaned_data['reviewer']
        return ','.join(reviewer)

    def clean_sql_content(self):
        sql_content = self.cleaned_data['sql_content'].rstrip()
        if sql_content[-1] != ';':
            raise forms.ValidationError('sql 语句没有用；结尾')
        return sql_content