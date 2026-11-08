import random
from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from players.models import Category, Player, PlayerSkills, Skills

SKILLS = {
    "Technical": ["Passing", "Dribbling", "First touch", "Shooting"],
    "Physical": ["Speed", "Stamina", "Strength"],
    "Tactical": ["Positioning", "Vision", "Pressing"],
    "Mental": ["Leadership", "Composure"],
}
PLAYERS = [
    ("Mueller", "Thomas", "Munich"), ("Neuer", "Manuel", "Munich"), ("Kimmich", "Joshua", "Rottweil"),
    ("Musiala", "Jamal", "Stuttgart"), ("Gnabry", "Serge", "Stuttgart"), ("Goretzka", "Leon", "Bochum"),
    ("Davies", "Alphonso", "Edmonton"), ("Kane", "Harry", "London"), ("Upamecano", "Dayot", "Evreux"),
    ("Coman", "Kingsley", "Paris"), ("Sane", "Leroy", "Essen"),
]


class Command(BaseCommand):
    help = "Seed demo data (idempotent: --mode refresh wipes first, --mode clear only wipes)."

    def add_arguments(self, parser):
        parser.add_argument("--mode", default="refresh", choices=["refresh", "clear"])
        parser.add_argument("--admin", action="store_true", help="Also create admin/admin user if missing")

    def handle(self, *args, **opts):
        if opts["mode"] in ("refresh", "clear"):
            PlayerSkills.objects.all().delete()
            Skills.objects.all().delete()
            Player.objects.all().delete()
            Category.objects.all().delete()
        if opts["mode"] == "clear":
            return
        rng = random.Random(7)
        skills = []
        for cat, names in SKILLS.items():
            c = Category.objects.create(name=cat)
            skills += [Skills.objects.create(skill_name=n, comment=f"{n} ability", category=c) for n in names]
        for i, (name, first, city) in enumerate(PLAYERS):
            p = Player.objects.create(
                name=name, first_name=first, address=f"{10 + i} Main Street", post_code=f"8{i:04d}",
                city=city, society="FC Demo", date_of_birth=date(1990 + i % 10, 1 + i % 12, 1 + i),
                phone_number=f"49170{1000000 + i}", email_address=f"{first.lower()}@example.com",
            )
            for s in skills:
                PlayerSkills.objects.create(player=p, skill=s, value=rng.randint(2, 5),
                                            modified_by="seed", modified_at=timezone.now())
        if opts["admin"] and not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin12345")
            self.stdout.write("Created demo user admin / admin12345 (change it!)")
        self.stdout.write(self.style.SUCCESS("Seed complete."))
