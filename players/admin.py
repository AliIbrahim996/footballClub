from django.contrib import admin
from django.utils import timezone

from .models import Category, Player, PlayerSkills, Plans, Skills

admin.site.site_header = "Football Club management"
admin.site.site_title = "Football Club"
admin.site.index_title = "Administration"


class PlayerSkillsInline(admin.TabularInline):
    model = PlayerSkills
    readonly_fields = ["modified_by", "modified_at"]
    extra = 0


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ["name", "first_name", "city", "society"]
    search_fields = ["name", "first_name", "city"]
    inlines = [PlayerSkillsInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, PlayerSkills):
                obj.modified_by = request.user.username
                obj.modified_at = timezone.now()
            obj.save()
        formset.save_m2m()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Plans)
class PlansAdmin(admin.ModelAdmin):
    list_display = ["title", "created_by", "created_at", "comment"]


@admin.register(Skills)
class SkillsAdmin(admin.ModelAdmin):
    list_display = ["category", "skill_name", "comment"]


@admin.register(PlayerSkills)
class PlayerSkillsAdmin(admin.ModelAdmin):
    list_display = ["player", "skill", "value", "modified_by"]
    readonly_fields = ["modified_by", "modified_at"]

    def save_model(self, request, obj, form, change):
        obj.modified_by = request.user.username
        obj.modified_at = timezone.now()
        super().save_model(request, obj, form, change)
