from django.contrib import admin
from .models import Request, PendingSale

# Register your models here.
class PendingSaleAdmin(admin.ModelAdmin):
    readonly_fields=('created',)

class RequestAdmin(admin.ModelAdmin):
    readonly_fields=('created',)

admin.site.register(Request, RequestAdmin)
admin.site.register(PendingSale, PendingSaleAdmin)
