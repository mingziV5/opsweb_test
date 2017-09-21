from django.views.generic import View, ListView
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from resources.server.models import Server, ServerStatus
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import QueryDict
import datetime
import traceback

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
