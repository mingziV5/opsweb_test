from django.views.generic import View, ListView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from resources.idc.models import Server
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
            s.save()
        return HttpResponse(" ")

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