from django.http import JsonResponse, QueryDict
from django.views.generic import View, TemplateView, ListView
from django.shortcuts import reverse, redirect
from django.utils.http import urlquote_plus
from monitor.influx.models import Graph
from monitor.influx.forms import CreateGraphForm, UpdateGraphForm
from monitor.influx.influxdbCli import influxdbCli
from resources.product.models import Product
from resources.server.models import Server
from opsweb.utils import GetLogger
import json
import traceback


'''
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
    template_name = 'influx/product_graph_test.html'

    def get_context_data(self, **kwargs):
        context = super(ProductGraphView, self).get_context_data(**kwargs)
        try:
            cli = influxdbCli()
            cli.query()
            context['series'] = json.dumps(cli.series)
            context['categories'] =cli.categories
        except:
            GetLogger().get_logger().error(traceback.format_exc())
        return context

class ProductGraphView(TemplateView):
    template_name = "influx/product_graphs.html"

    def get_context_data(self, **kwargs):
        context = super(ProductGraphView, self).get_context_data(**kwargs)
        context["products"] = self.get_product()
        return context

    def get_product(self):
        products = Product.objects.all()
        ret = []
        #{"id":2, "name":"ms-web"}
        for obj in products.filter(pid__exact=0):
            for product in products.filter(pid__exact=obj.id):
                ret.append({
                    "id": product.id,
                    "name":"{}->{}".format(obj.service_name, product.service_name)
                })
        return ret
'''
class  ProductGraphView(TemplateView):
    template_name = "influx/product_graphs.html"

    def get_context_data(self, **kwargs):
        context = super(ProductGraphView, self).get_context_data(**kwargs)
        context["products"] = self.get_product()
        return context

    def get_product(self):
        products = Product.objects.all()
        ret = []
        # 数据格式
        # {"id":2, "name": "ms-web"}
        '''
        for obj in products.filter(pid__exact=0):
            for product in products.filter(pid__exact=obj.id):
                ret.append({
                    "id": product.id,
                    "name": "{}->{}".format(obj.service_name, product.service_name)
                })
        '''
        #循环一次
        for product in products.exclude(pid__exact=0):
            pervious_service_name = products.get(id=product.pid).service_name
            ret.append({
                "id": product.id,
                "name": "{}->{}".format(pervious_service_name, product.service_name)
            })
        return ret

class InfluxApiView(View):
    '''
    def get(self, request):
        # graph_id=7&graph_time=30m
        ret = {"status":0}
        graph_id = request.GET.get("graph_id", None)
        graph_time = request.GET.get("graph_time", None)
        product_id = request.GET.get("product_id", None)

        try:
            graph_obj = Graph.objects.get(pk=graph_id)
        except:
            ret["status"] = 1
            ret["errmsg"] = "graph 不存在"
            return JsonResponse(ret)

        try:
            product_obj = Product.objects.get(pk=product_id)
            if product_obj.pid == 0:
                ret["status"] = 1
                ret["errmsg"] = "业务线异常"
                return JsonResponse(ret)
        except:
            ret["status"] = 1
            ret["errmsg"] = "业务线异常"
            return JsonResponse(ret)


        client = influxdbCli()
        client.hostnames = [s["hostname"] for s in Server.objects.filter(server_purpose__exact=product_obj.id).values("hostname")]
        client.graph_obj = graph_obj
        client.graph_time = graph_time

        client.query()
        ret["series"] = client.series
        ret["categories"] = client.categories
        return JsonResponse(ret,safe=False)
    '''

    def get(self, request):
        #数据请求格式 graph_id=7 & graph_time=30m &product_id=1
        ret = {"status": 0}
        graph_id = request.GET.get("graph_id", None)
        graph_time = request.GET.get("graph_time", None)
        product_id = request.GET.get("product_id", None)

        try:
            graph_obj = Graph.objects.get(pk=graph_id)
        except:
            GetLogger().get_logger().error(traceback.format_exc())
            ret['status'] = 1
            ret['errmsg'] = "graph 不存在"
            return JsonResponse(ret)

        try:
            product_obj = Product.objects.get(pk=product_id)
            if product_obj.pid == 0:
                ret['status'] = 1
                ret['errmsg'] = "顶级业务线没有图形"
                return JsonResponse(ret)
        except:
            GetLogger().get_logger().error(traceback.format_exc())
            ret['status'] = 1
            ret['errmsg'] = '业务线异常'
            return JsonResponse(ret)

        client = influxdbCli()
        client.hostnames = [s["hostname"] for s in Server.objects.filter(server_purpose__exact=product_obj.id).values('hostname')]
        client.graph_obj = graph_obj
        client.graph_time = graph_time

        client.query()
        ret['series'] = client.series
        ret['categories'] = client.categories
        return JsonResponse(ret, safe=False)

class GraphGetView(View):
    def get(self, request):
        productid = request.GET.get("id",None)
        outside = request.GET.get("outside", False)

        try:
            product_obj = Product.objects.get(pk=productid)
            if product_obj.pid == 0:
                return JsonResponse([], safe=False)
        except Product.DoesNotExist:
            return JsonResponse([], safe=False)

        queryset = Graph.objects.values()
        if outside:
            queryset = queryset.exclude(product__id=productid)
        else:
            queryset = queryset.filter(product__id=productid)
        return JsonResponse(list(queryset), safe=False)

class CreateGrapView(TemplateView):
    template_name = 'influx/create_graph.html'

    def get_context_data(self, **kwargs):
        context = super(CreateGrapView, self).get_context_data(**kwargs)
        try:
            cli = influxdbCli()
            context['measurements'] = cli.measurements
        except:
            GetLogger().get_logger().error(traceback.format_exc())
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

class TestGrapView(View):
    def get(self, request):
        ret = {}
        measurement = request.GET.get('measurement', None)
        field_expression = request.GET.get('field_expression', None)
        measurement = measurement.strip()
        field_expression = field_expression.strip()
        cli = influxdbCli()
        if not measurement or measurement not in cli.measurements:
            ret['status'] = 1
            ret['errmsg'] = 'measurement不能空或者数据不正确'
            return JsonResponse()
        try:
            series = cli.get_series(measurement, field_expression)
            ret['data'] = series
            ret['status'] = 0
        except:
            GetLogger().get_logger().error(traceback.format_exc())
        return JsonResponse(ret, safe=False)


class ManagerGraphView(ListView):
    template_name = 'influx/graph_manager.html'
    model = Graph

    #取出在productid业务线内的graph
    def get_queryset(self):
        queryset = super(ManagerGraphView, self).get_queryset()
        productid = self.request.GET.get('product')
        if productid:
            queryset = Graph.objects.filter(product__id=productid)
        else:
            return None
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ManagerGraphView, self).get_context_data(**kwargs)
        try:
            #context['products'] = Product.objects.exclude(pid=0)
            products = Product.objects.exclude(pid=0).values('id', 'pid', 'service_name')
            for p in products:
                print(p)
                p_service_name = Product.objects.get(id=p['pid']).service_name
                p['pid'] = p_service_name
            context['products'] = products
        except Exception as e:
            GetLogger().get_logger().error(traceback.format_exc())
        context.update(self.get_args())
        return context

    def get_args(self):
        productid = self.request.GET.get('product', None)
        try:
            return {'productid': int(productid)}
        except:
            GetLogger().get_logger().error(traceback.format_exc())
            return {}

class GraphListView(ListView):
    template_name = 'influx/graph_list.html'
    model = Graph
    paginate_by = 10
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

class GraphProductModifyView(View):

    #不在业务线下的graph
    def get(self, request):
        productid = request.GET.get('id', None)
        if productid:
            try:
                graphs = Graph.objects.exclude(product__id=productid).values('id', 'title')
            except:
                GetLogger().get_logger().error(traceback.format_exc())
        return JsonResponse(list(graphs), safe=False)

    def post(self, request):
        response = {}
        graphid = request.POST.get('graph_id')
        productid = request.POST.get('productid')
        try:
            product_obj = Product.objects.get(pk=productid)
            graph_obj = Graph.objects.get(pk=graphid)
        except:
            GetLogger().get_logger().error(traceback.format_exc())
            response['status'] = 1
            response['errmsg'] = '数据输入出错了，找不到对应模型'
            return JsonResponse(response)
        if product_obj.pid == 0:
            response['status'] = 1
            response['errmsg'] = '请选择次级业务线'
            return JsonResponse(response)
        try:
            #product_obj.graph_set.add(graph_obj)
            graph_obj.product.add(product_obj.id)
            graph_obj.save()
        except:
            GetLogger().get_logger().error(traceback.format_exc())
            response['status'] = 1
            response['errmsg'] = '添加关系出错了'
            return JsonResponse(response)
        response['status'] = 0
        return JsonResponse(response)

    def delete(self, request):
        response = {}
        data = QueryDict(request.body)
        graphid = data.get('graph_id', None)
        productid = data.get('productid', None)
        try:
            product_obj = Product.objects.get(pk=productid)
            graph_obj = Graph.objects.get(pk=graphid)
        except:
            GetLogger().get_logger().error(traceback.format_exc())
            response['status'] = 1
            response['errmsg'] = '数据输入错误，找不到对应模型'
            return JsonResponse(response)
        try:
            graph_obj.product.remove(product_obj.id)
            graph_obj.save()
        except:
            GetLogger().get_logger().error(traceback.format_exc())
            response['status'] = 1
            response['errmsg'] = '移除关系出错'
            return JsonResponse(response)
        response['status'] = 0
        return JsonResponse(response)

class GraphModifyView(TemplateView):
    template_name = 'influx/update_graph.html'

    def get_context_data(self, **kwargs):
        context = super(GraphModifyView, self).get_context_data(**kwargs)
        graph_id = self.request.GET.get('graphid', None)
        try:
            graph_obj = Graph.objects.get(pk=graph_id)
        except:
            GetLogger().get_logger().error(traceback.format_exc())
        context['graph_obj'] = graph_obj
        try:
            cli = influxdbCli()
        except:
            GetLogger().get_logger().error(traceback.format_exc())
        context['measurements'] = cli.measurements
        return context

    def post(self, request):
        next_url = urlquote_plus(request.GET.get('next', None) if request.GET.get('next', None) else reverse('influx_graph_list'))
        form = UpdateGraphForm(request.POST)
        if form.is_valid():
            try:
                graph_id = form.cleaned_data.get('id')
                graph_obj = Graph.objects.get(pk=graph_id)
                graph_obj.title = form.cleaned_data.get('title')
                graph_obj.subtitle = form.cleaned_data.get('subtitle')
                graph_obj.unit = form.cleaned_data.get('unit')
                graph_obj.measurement = form.cleaned_data.get('measurement')
                graph_obj.auto_hostname = form.cleaned_data.get('auto_hostname')
                graph_obj.field_expression = form.cleaned_data.get('field_expression')
                graph_obj.tooltip_formatter = form.cleaned_data.get('tooltip_formatter')
                graph_obj.yaxis_formatter = form.cleaned_data.get('yaxis_formatter')
                graph_obj.save()
                return redirect('success', next=next_url)
            except Exception as e:
                GetLogger().get_logger().error(traceback.format_exc())
                return redirect('error', next=next_url, msg=e.args)
        else:
            return redirect('error', next=next_url, msg=form.errors.as_json())

