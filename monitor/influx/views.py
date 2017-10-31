from django.http import JsonResponse
from django.views.generic import View, TemplateView, ListView
from django.shortcuts import reverse, redirect
from django.utils.http import urlquote_plus
from monitor.influx.models import Graph
from monitor.influx.forms import CreateGraphForm
from monitor.influx.influxdbCli import influxdbCli
from resources.product.models import Product
from opsweb.utils import GetLogger
import json
import traceback

class InfluxApiView(View):
    def get(self, request):
        ret = {}
        ret['status'] = 0
        cli = influxdbCli()
        cli.query()
        ret['series'] = cli.series
        ret['categories'] = cli.categories
        return JsonResponse(ret, safe=False)

class ProductGraphView(TemplateView):
    template_name = 'influx/product_graph.html'

    def get_context_data(self, **kwargs):
        context = super(ProductGraphView, self).get_context_data(**kwargs)
        try:
            cli = influxdbCli()
            cli.query()
            context['series'] = json.dumps(cli.series)
            context['categories'] =cli.categories
        except:
            pass
        return context

class CreateGrapView(TemplateView):
    template_name = 'influx/create_graph.html'

    def get_context_data(self, **kwargs):
        context = super(CreateGrapView, self).get_context_data(**kwargs)
        try:
            cli = influxdbCli()
            context['measurements'] = cli.measurements
        except:
            pass
        return context

    def post(self, request):
        next_url = urlquote_plus(request.GET.get('next', None) if request.GET.get('next', None) else reverse('influx_graph_list'))
        form = CreateGraphForm(request.POST)
        if form.is_valid():
            try:
                graph = Graph(**form.cleaned_data)
                graph.save()
                return redirect('success', next=next_url)
            except Exception as e:
                return redirect('error', next=next_url, msg=e.args)
        else:
            return redirect('error', next=next_url, msg=form.errors.as_json())

class ManagerGraphView(ListView):
    template_name = 'influx/graph_manage.html'
    model = Graph

    def get_context_data(self, **kwargs):
        context = super(ManagerGraphView, self).get_context_data(**kwargs)
        try:
            #context['products'] = Product.objects.exclude(pid=0)
            products = Product.objects.exclude(pid=0)
            for p in products:
                p_service_name = Product.objects.get(id=p.pid).service_name
                p.pid = p_service_name
            context['products'] = products
        except Exception as e:
            GetLogger().get_logger().error(traceback.format_exc())
        return context

class GraphListView(ListView):
    template_name = 'influx/graph_list.html'
    model = Graph
    paginate_by = 10
    before_range_num = 4
    after_range_num = 5

    def get_queryset(self):
        queryset = super(GraphListView, self).get_queryset()
        queryset = Graph.objects.all()
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
        context = super(GraphListView, self).get_context_data(**kwargs)
        context['page_range_obj'] = self.get_page_range(context['page_obj'])
        #处理查询条件
        search_data = self.request.GET.copy()
        try:
            search_data.pop("page")
        except:
            pass
        context.update(search_data.dict())
        context['search_data'] = "&" + search_data.urlencode()
        return context