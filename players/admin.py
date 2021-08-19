from django.contrib import admin
from .models import *


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = ugettext_lazy('Player')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = ugettext_lazy('Category')


@admin.register(Plans)
class PlansAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = ugettext_lazy('Plans')


@admin.register(Skills)
class SkillsAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = ugettext_lazy('Skills')


@admin.register(PlayerSkills)
class PlayerSkills(admin.ModelAdmin):
    class Meta:
        verbose_name = ugettext_lazy('Player_Skills')
