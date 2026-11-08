"""Data migration: put all pre-multi-tenant rows (and users) into one default club."""
from django.db import migrations
from django.utils import timezone


def forwards(apps, schema_editor):
    Club = apps.get_model("players", "Club")
    Membership = apps.get_model("players", "Membership")
    User = apps.get_model("auth", "User")
    models = [apps.get_model("players", n) for n in ("Category", "Skills", "Player", "Plans")]
    if not any(m.objects.filter(club__isnull=True).exists() for m in models) and not User.objects.exists():
        return
    # Existing installs keep working: the default club is on a lifetime "active" plan.
    club, _ = Club.objects.get_or_create(name="Default club", defaults={"status": "active", "created_at": timezone.now()})
    for m in models:
        m.objects.filter(club__isnull=True).update(club=club)
    for user in User.objects.filter(membership__isnull=True):
        Membership.objects.create(user=user, club=club, role="owner" if user.is_staff else "coach")


class Migration(migrations.Migration):
    dependencies = [("players", "0035_clubs_and_memberships"), ("auth", "0012_alter_user_first_name_max_length")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
