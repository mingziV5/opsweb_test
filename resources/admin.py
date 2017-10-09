from django.contrib import admin
from resources.idc.models import Idc
from resources.product.models import Product
from resources.server.models import Server, ServerStatus
# Register your models here.

class IdcAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name', 'contact')
    search_fields = ('name', 'full_name')

class ServerAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'inner_ip')
    search_fields = ('hostname', 'inner_ip')
    list_filter = ('check_update_time', )
    date_hierarchy = 'check_update_time'
    #filter_horizontal = ('hostname', )

admin.site.register(Idc, IdcAdmin)
admin.site.register(Product)
admin.site.register(Server, ServerAdmin)
admin.site.register(ServerStatus)

