from django.db import models
from resources.product.models import Product

class Graph(models.Model):
    title = models.CharField("图形标题", max_length=50, null=False)
    subtitle = models.CharField("图形子标题", max_length=50, null=True)
    unit = models.CharField("数据点格式化后的单位, y轴格式化后的单位", max_length=10, null=False)
    measurement = models.CharField("influx 表名", max_length=32, null=False)
    auto_hostname = models.BooleanField("是否从业务线取主机名作为条件", null=False, default=True)
    field_expression = models.CharField("influx sql where 条件", max_length=100, null=True)
    product = models.ManyToManyField(Product, verbose_name="与业务线表多对多关联")
    tooltip_formatter = models.CharField("对tooltip进行格式化", max_length=100, null=True)
    yaxis_formatter = models.CharField("对y轴进行格式化", max_length=100, null=True)

    class Meta:
        db_table = "monitor_influx_graph"
        ordering = ['id']