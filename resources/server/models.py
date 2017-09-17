'''
from django.db import models
from resources.idc.models import Idc

class Server(models.Model):
    supplier = models.IntegerField(null=True)
    manufacturers = models.CharField(max_length=50, null=True)
    manufacture_date = models.DateField(null=True)
    server_type = models.CharField(max_length=20, null=True)
    sn = models.CharField(max_length=60, db_index=True, null=True)
    idc = models.ForeignKey(Idc, null=True)
    os = models.CharField(max_length=50, null=True)
    hostname = models.CharField(max_length=50, db_index=True, null=True)
    inner_ip = models.CharField(max_length=32, null=True, unique=True)
    mac_address = models.CharField(max_length=50, null=True)
    ip_info = models.CharField(max_length=255, null=True)
    server_cpu = models.CharField(max_length=250, null=True)
    server_disk = models.CharField(max_length=100, null=True)
    server_mem = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=100,db_index=True, null=True)
    remark = models.TextField(null=True)
    service_id = models.IntegerField(db_index=True, null=True)
    server_purpose = models.IntegerField(db_index=True, null=True)
    check_update_time = models.DateTimeField(null=True)
    vm_status = models.IntegerField(db_index=True, null=True)
    uuid = models.CharField(max_length=100, db_index=True,null=True)

    def __str__(self):
        return self.hostname

    class Meta:
        db_table = 'resources_server'
        ordering = ['id']
'''