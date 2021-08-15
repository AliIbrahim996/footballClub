from django.contrib import admin
from .models import *

admin.site.site_header = 'Verwaltung'
admin.site.site_title = 'Verwaltung'
admin.site.index_title = 'Verwaltung'


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass


@admin.register(Skills)
class SkillAdmin(admin.ModelAdmin):
    pass