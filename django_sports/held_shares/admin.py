from django.contrib import admin
from .models import InvestedShare, InvestedGame

class ShareAdmin(admin.ModelAdmin):
    readonly_fields = ('created', )

class GameAdmin(admin.ModelAdmin):
    readonly_fields = ('created', )

# Register your models here.
admin.site.register(InvestedShare, ShareAdmin)
admin.site.register(InvestedGame, GameAdmin)
