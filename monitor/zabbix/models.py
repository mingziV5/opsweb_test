from django.db import models
from resources.server.models import Server


# Create your models here.
class ZabbixHost(models.Model):
    hostid = models.IntegerField("zabbix hostid", db_index=True)
    host = models.CharField("zabbix hostname", max_length=50, null=True)
    ip = models.CharField("zabbix ip", max_length=32, db_index=True)
    server = models.OneToOneField(Server)
    updatetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} {}".format(self.hostid, self.host)

    class Meta:
        db_table = "zabbix_cache_host"