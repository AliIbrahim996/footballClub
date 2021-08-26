"""@package Players application
ModelAdmin objects
The ModelAdmin class is the representation of a model in the admin interface
"""
from django.contrib import admin
from .models import *
from django.utils.translation import ugettext_lazy as tran


class PlayerSkillsInlineAdmin(admin.TabularInline):
    model = PlayerSkills


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """
        Documentation for PlayerAdmin:
        a model class to register Player model with the ModelAdmin
    """
    list_display = ['name', 'first_name', 'address']
    inlines = (PlayerSkillsInlineAdmin,)

    class Meta:
        """
          Documentation for Meta class:
          a  class that define a meta verbose name for Class PlayerAdmin
        """
        verbose_name = tran('Player_model')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Documentation for CategoryAdmin:
    a model class to register Category model with the ModelAdmin
    """
    list_display = ['name']
    actions = ["silent_delete"]

    class Meta:
        """
        Documentation for Meta class:
        a  class that define a meta verbose name for Class CategoryAdmin
        """
        verbose_name = tran('Category_model')


@admin.register(Plans)
class PlansAdmin(admin.ModelAdmin):
    """
    Documentation for PlansAdmin:
    a model class to register Plans model with the ModelAdmin
    """
    list_display = ['created_by', 'created_at', 'comment', 'image']

    class Meta:
        """
        Documentation for Meta class:
        a  class that define a meta verbose name for Class PlansAdmin
        """
        verbose_name = tran('Plans_model')


@admin.register(Skills)
class SkillsAdmin(admin.ModelAdmin):
    """
    Documentation for SkillsAdmin:
    a model class to register Skills model with the ModelAdmin
    """
    list_display = ['category', 'skill_name', 'comment']

    class Meta:
        """
        Documentation for Meta class:
        a  class that define a meta verbose name for Class SkillsAdmin
        """
        verbose_name = tran('Skills_model')


@admin.register(PlayerSkills)
class PlayerSkills(admin.ModelAdmin):
    """
    Documentation for PlayerSkills:
     a model class to register PlayerSkills model with the ModelAdmin
    """
    list_display = ['player', 'skill', 'value','modified_by']

    class Meta:
        """
         Documentation for Meta class:
         a  class that define a meta verbose name for Class PlayerSkills
        """
        verbose_name = tran('Player_Skills_model')
