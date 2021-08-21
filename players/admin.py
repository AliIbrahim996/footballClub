from django.contrib import admin
from .models import *
from django.utils.translation import ugettext_lazy as tran


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = tran('Player_model')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = tran('Category_model')


@admin.register(Plans)
class PlansAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = tran('Plans_model')


@admin.register(Skills)
class SkillsAdmin(admin.ModelAdmin):
    class Meta:
        verbose_name = tran('Skills_model')


@admin.register(PlayerSkills)
class PlayerSkills(admin.ModelAdmin):
    class Meta:
        verbose_name = tran('Player_Skills_model')
