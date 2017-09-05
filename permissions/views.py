from django.views.generic import ListView,TemplateView
from django.contrib.auth.models import Permission, ContentType
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

class PermissionListView(LoginRequiredMixin, ListView):
    template_name = "permissions_list.html"
    model = Permission
    paginate_by = 10
    before_range_num = 4
    after_range_num = 5
    ordering = 'id'

    def get_queryset(self):
        queryset = super(PermissionListView, self).get_queryset()
        queryset = Permission.objects.all()
        return queryset

    def get_page_range(self, page_obj):
        current_index = page_obj.number
        start = current_index - self.before_range_num
        end = current_index + self.after_range_num
        if start <= 0:
            start = 1
        if end > page_obj.paginator.num_pages:
            end = page_obj.paginator.num_pages
        return range(start, end + 1)

    def get_context_data(self, **kwargs):
        context = super(PermissionListView, self).get_context_data(**kwargs)
        context['page_range_obj'] = self.get_page_range(context['page_obj'])
        return context

class PermissionAddView(LoginRequiredMixin, TemplateView):
    template_name = "permission_add.html"

    def get_context_data(self, **kwargs):
        context = super(PermissionAddView, self).get_context_data(**kwargs)
        contentType_objs = ContentType.objects.values('id', 'app_label', 'model')

        context['contenttypes'] = list(contentType_objs)

        return context

    def post(self, request):
        content_type_id = request.POST.get('content_type', None)
        codename = request.POST.get('codename', None)
        name = request.POST.get('name', None)
        #content_type = ContentType.objects.get_for_model()

        if not codename or codename.find(" ") >= 0:
            msg = "codename 不合法"
            return redirect("error", next="permission_add", msg=msg)
        try:
            content_type = ContentType.objects.get(pk=content_type_id)
        except ContentType.DoseNotExist:
            return redirect("error", next='permission_add', msg='模型不存在')

        try:
            #Permission.objects.create(codename=codename, name=name, content_type_id=content_type_id)
            Permission.objects.create(codename=codename, name=name, content_type=content_type)
            return redirect("success", next="permission_list")
        except Exception as e:
            print(e)
            msg = "添加权限出错"
            return redirect("error", next="permission_add", msg=msg)

