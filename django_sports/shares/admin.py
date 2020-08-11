from django.contrib import admin
from .models import Share, Category, Event, Game

# class ShareAdmin(admin.ModelAdmin):
#     readonly_fields = ('amount', )

admin.site.register(Category)
admin.site.register(Event)
admin.site.register(Game)

class ShareAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'tradedAmount')

admin.site.register(Share, ShareAdmin)
