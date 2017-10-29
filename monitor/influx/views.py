from django.http import JsonResponse
from django.views.generic import View, TemplateView, ListView
from django.shortcuts import reverse, redirect
from django.utils.http import urlquote_plus
from influxdb import InfluxDBClient
from monitor.influx.models import Graph
from monitor.influx.forms import CreateGraphForm
import json
import time

class influxdbCli():
    def __init__(self):
        self.client = InfluxDBClient("192.168.1.201", database="collectd")
        #x轴数据
        self.categories = []
        #图形数据点
        self.series = []
        self.measurements = self.get_measurements()

    def get_measurements(self):
        measurements = self.client.query("show measurements").get_points()
        return [m['name'] for m in measurements]

    def process_time(self, categories):
        ret = []
        format_str = "%Y-%m-%d %H:%M:%S"
        for point in categories:
            ret.append(time.strftime(format_str, time.localtime(point)))
        return ret

    def query(self):
        hostnames = ["ubuntu-xenial"]
        sql = ""
        for hostname in hostnames:
            sql += """select mean(value) as value \
                from interface_tx \
                where time > now() - 10m \
                and instance = 'enp0s8' \
                and type = 'if_octets' \
                and host = '{}' \
                group by time(10s) order by time desc;""".format(hostname)
        result = self.client.query(sql, epoch='s')
        #判断hostnames长度
        if len(hostnames) > 1:
            for index, hostname in enumerate(hostnames):
                self.process_data(hostname, result[index].get_points())
        else:
            self.process_data(hostnames[0], result.get_points())

    def process_data(self, hostname, data_points):
        serie = {}
        serie['name'] = hostname
        serie['type'] = 'line'
        serie['data'] = []
        categories = []
        for point in data_points:
            serie['data'].insert(0, point['value'])
            categories.insert(0, point['time'])
        self.series.append(serie)
        if not self.categories:
            self.categories = categories

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

class GraphListView(ListView):
    template_name = 'influx/graph_list.html'
    model = Graph