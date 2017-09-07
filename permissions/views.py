from django.views.generic import ListView,TemplateView
from django.contrib.auth.models import Permission, ContentType
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.db import connection
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
        #获得搜索内容
        queryset = Permission.objects.all()
        search_value = self.request.GET.get('search_value', None)
        if search_value:
            #Q连表查询 |：OR ~: != &: AND
            queryset = queryset.filter(Q(codename__contains=search_value)|Q(content_type_id__model__contains=search_value))
            #print(queryset.filter(Q(codename__contains=search_value)|Q(content_type_id__model__contains=search_value)).query)
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
        context = super(PermissionListView, self).get_context_data(**kwargs)
        context['page_range_obj'] = self.get_page_range(context['page_obj'])
        #处理查询条件
        search_data = self.request.GET.copy()
        try:
            search_data.pop("page")
        except:
            pass
        context.update(search_data.dict())
        context['search_data'] = "&" + search_data.urlencode()
        print(context)
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



