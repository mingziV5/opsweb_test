from django.views.generic import View, ListView, TemplateView
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from resources.server.models import Server, ServerStatus
from resources.product.models import Product
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils.http import urlquote_plus
import datetime

@csrf_exempt
def ServerInfoAutoReport(request):
    if request.method == "POST":
        data = request.POST.dict()
        data['check_update_time'] = datetime.datetime.now()
        try:
            Server.objects.get(uuid__exact=data['uuid'])
            Server.objects.filter(uuid=data['uuid']).update(**data)
            '''
            s.hostname = data['hostanme']
            s.check_update_time = datatime.now()
            s.save(update_fields=['hostname'])
            '''
        except Server.DoesNotExist:
            s = Server(**data)
            server_status_obj = ServerStatus.objects.get(pk=1)
            s.status = server_status_obj
            s.save()
        return HttpResponse("success")
    else:
        return HttpResponse("method error")

class ServerListView(ListView):
    model = Server
    paginate_by = 10
    template_name = "server/server_list.html"
    before_range_num = 4
    after_range_num = 5

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
        context = super(ServerListView, self).get_context_data(**kwargs)
        context['page_range_obj'] = self.get_page_range(context['page_obj'])
        return context

class ModifyServerStatusView(LoginRequiredMixin, View):
    def get(self, request):
        sid = request.GET.get('sid', None)
        server_status_objs = ServerStatus.objects.all()
        try:
            server_obj = Server.objects.get(pk=sid)
        except Server.DoesNotExist:
            pass
        return JsonResponse(list(server_status_objs.values('id', 'name')), safe=False)

    def patch(self, request):
        response = {'status': 0}
        data = QueryDict(request.body)
        sid = data.get('sid', None)
        ssid = data.get('ssid', None)
        try:
            server_obj = Server.objects.get(pk=sid)
        except Server.DoesNotExist:
            response['status'] = 1
            response['errmsg'] = '服务器不存在'
            return JsonResponse(response)
        try:
            server_status_obj = ServerStatus.objects.get(pk=ssid)
        except ServerStatus.DoesNotExist:
            response['status'] = 1
            response['errmsg'] = '服务器状态不存在'
            return JsonResponse(response)
        try:
            server_obj.status = server_status_obj
            server_obj.save()
        except:
            response['status'] = 1
            response['errmsg'] = '更改服务器状态出错'
            return JsonResponse(response)
        return JsonResponse(response)

class GetServerListView(View):
    def get(self, request):
        server_purpose = request.GET.get("server_purpose", None)
        #获取某台机器的所有信息
        #获取某个业务线下的所有机器列表
        if server_purpose:
            queryset = Server.objects.filter(server_purpose=server_purpose).values("id", "hostname", "inner_ip")
            #queryset = Server.objects.values("id", "hostname", "inner_ip")
            return JsonResponse(list(queryset), safe=False)
        return JsonResponse([], safs=False)

class ServerModifyProductView(TemplateView):
    template_name = "server/server_modify_product.html"

    def get_context_data(self, **kwargs):
        context = super(ServerModifyProductView, self).get_context_data(**kwargs)
        server_id = self.request.GET.get("id", None)
        context['server'] = get_object_or_404(Server, pk=server_id)
        context['products'] = Product.objects.filter(pid=0)
        return context

    def post(self, request):
        next_url = request.GET.get("next", None) if request.GET.get('next', None) else 'server_list'
        server_id = request.POST.get('id', None)
        service_id = request.POST.get('service_id', None)
        server_purpose = request.POST.get('server_purpose', None)

        try:
            server_obj = Server.objects.get(pk=server_id)
            product_service_id = Product.objects.get(pk=service_id)
            product_server_purpose = Product.objects.get(pk=server_purpose)
        except:
            return redirect("error", next="server_list", msg="传参错误")

        if product_server_purpose.pid != product_service_id.id:
            return Http404
        server_obj.service_id = product_service_id.id
        server_obj.server_purpose = product_server_purpose.id
        server_obj.save(update_fields=["service_id", "server_purpose"])
        return redirect(reverse("success", kwargs={"next": urlquote_plus(next_url)}))