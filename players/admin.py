## @package Players
#  ModelAdmin objects
#
#  The ModelAdmin class is the representation of a model in the admin interface

from django.contrib import admin
from .models import *
from django.utils.translation import ugettext_lazy as tran


@admin.register(Player)
## Documentation for PlayerAdmin.
#
#  a model class to register Player model with the ModelAdmin
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'first_name', 'address']

    ## Documentation for Meta class.
    #
    #  a  class that define a meta verbose name for Class PlayerAdmin
    class Meta:
        verbose_name = tran('Player_model')


@admin.register(Category)
## Documentation for CategoryAdmin.
#
#  a model class to register Category model with the ModelAdmin
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

    ## Documentation for Meta class.
    #
    #  a  class that define a meta verbose name for Class CategoryAdmin
    class Meta:
        verbose_name = tran('Category_model')


@admin.register(Plans)
## Documentation for PlansAdmin.
#
#  a model class to register Plans model with the ModelAdmin
class PlansAdmin(admin.ModelAdmin):
    list_display = ['created_by', 'created_at', 'comment', 'image']

    ## Documentation for Meta class.
    #
    #  a  class that define a meta verbose name for Class PlansAdmin
    class Meta:
        verbose_name = tran('Plans_model')


@admin.register(Skills)
class SkillsAdmin(admin.ModelAdmin):
    list_display = ['category', 'skill_name', 'comment']

    class Meta:
        verbose_name = tran('Skills_model')


@admin.register(PlayerSkills)
class PlayerSkills(admin.ModelAdmin):
    list_display = ['player', 'skill', 'value']

    class Meta:
        verbose_name = tran('Player_Skills_model')
