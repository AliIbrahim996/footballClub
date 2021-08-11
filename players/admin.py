from django.contrib import admin
from .models import Player

admin.site.site_header = 'Verwaltung'
admin.site.site_title = 'Verwaltung'
admin.site.index_title = 'Verwaltung'


@admin.register(Player)
class PersonAdmin(admin.ModelAdmin):
    pass
