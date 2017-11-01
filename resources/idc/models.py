from django.db import models

# Create your models here.
class Idc(models.Model):
    name = models.CharField("idc 字母简称", max_length=16, default="", unique=True)
    full_name = models.CharField("idc 中文全称", max_length=32, default="")
    address = models.CharField("具体地址", max_length=255, null=True)
    phone = models.CharField("机房联系电话", max_length=20, null=True)
    email = models.EmailField("机房Email", null=True)
    contact = models.CharField("机房联系人", max_length=32, null=True)

    class Meta:
        db_table = "resources_idc"
        ordering = ['id']

    def __str__(self):
        return self.full_name