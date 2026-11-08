import random
from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from players.models import Category, Club, Membership, Player, PlayerSkills, Skills

SKILLS = {
    "Technical": ["Passing", "Dribbling", "First touch", "Shooting"],
    "Physical": ["Speed", "Stamina", "Strength"],
    "Tactical": ["Positioning", "Vision", "Pressing"],
    "Mental": ["Leadership", "Composure"],
}
PLAYERS = [  # fictional demo squad
    ("Hartmann", "Lukas", "Berlin"), ("Okafor", "Daniel", "Hamburg"), ("Yilmaz", "Emre", "Cologne"),
    ("Novak", "Marek", "Munich"), ("Rahimi", "Omar", "Stuttgart"), ("Becker", "Jonas", "Leipzig"),
    ("Haddad", "Karim", "Dortmund"), ("Schulz", "Felix", "Bremen"), ("Costa", "Mateo", "Frankfurt"),
    ("Weber", "Tim", "Duesseldorf"), ("Nasser", "Yusuf", "Essen"),
]
DEMO_CLUB = "Demo FC"


class Command(BaseCommand):
    help = "Seed a demo club (--mode refresh recreates it, --mode clear only removes it)."

    def add_arguments(self, parser):
        parser.add_argument("--mode", default="refresh", choices=["refresh", "clear"])
        parser.add_argument("--admin", action="store_true", help="Also create the admin/admin12345 demo owner")

    def handle(self, *args, **opts):
        Club.objects.filter(name=DEMO_CLUB).delete()  # cascades to its players, skills and plans
        if opts["mode"] == "clear":
            return
        rng = random.Random(7)
        club = Club.objects.create(name=DEMO_CLUB, status=Club.ACTIVE)  # active so the demo never hits the paywall
        skills = []
        for cat, names in SKILLS.items():
            c = Category.objects.create(club=club, name=cat)
            skills += [Skills.objects.create(club=club, skill_name=n, comment=f"{n} ability", category=c) for n in names]
        for i, (name, first, city) in enumerate(PLAYERS):
            p = Player.objects.create(
                club=club, name=name, first_name=first, address=f"{10 + i} Main Street", post_code=f"8{i:04d}",
                city=city, society=DEMO_CLUB, date_of_birth=date(1990 + i % 10, 1 + i % 12, 1 + i),
                phone_number=f"49170{1000000 + i}", email_address=f"{first.lower()}@example.com",
            )
            for s in skills:
                PlayerSkills.objects.create(player=p, skill=s, value=rng.randint(2, 5),
                                            modified_by="seed", modified_at=timezone.now())
        if opts["admin"]:
            user, created = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True})
            if created:
                user.set_password("admin12345")
                user.save()
                self.stdout.write("Created demo user admin / admin12345 (change it!)")
            Membership.objects.update_or_create(user=user, defaults={"club": club, "role": Membership.OWNER})
        self.stdout.write(self.style.SUCCESS("Seed complete."))
