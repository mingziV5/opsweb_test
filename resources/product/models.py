from django.db import models

class Product(models.Model):
    service_name = models.CharField('业务线', max_length=32)
    module_letter = models.CharField('字母简称', max_length=10, db_index=True)
    op_interface = models.CharField('运维对接人', max_length=150)
    dev_interface = models.CharField('业务对接人', max_length=150)
    pid = models.IntegerField('上级业务线id', db_index=True)

    class Meta:
        verbose_name = '业务线'
        verbose_name_plural = verbose_name
        ordering = ['pid']

    def __str__(self):
        return self.service_name