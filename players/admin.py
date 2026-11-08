from django.contrib import admin
from django.utils import timezone

from .models import Category, Club, ContactMessage, Invitation, Membership, Player, PlayerSkills, Plans, Skills

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


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "trial_ends_at", "current_period_end", "created_at"]
    list_filter = ["status"]
    search_fields = ["name", "stripe_customer_id"]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "club", "role"]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ["email", "club", "role", "created_at", "accepted_at"]

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "club", "created_at", "handled"]
    list_filter = ["handled"]
    search_fields = ["name", "email", "club", "message"]
    readonly_fields = ["created_at"]
