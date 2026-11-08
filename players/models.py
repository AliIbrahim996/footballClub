"""@package Players application
Model objects.
A model is the single, definitive source of information about your data.
It contains the essential fields and behaviors of the data you’re storing.
Generally, each model maps to a single database table
The basics:
    * Each model is a Python class that subclasses django.db.models.Model.
    * Each attribute of the model represents a database field.
    * With all of this, Django gives you an automatically-generated database-access API; see [Making queries](https://docs.djangoproject.com/en/3.2/topics/db/queries/).
for more information visit: https://docs.djangoproject.com/en/3.2/topics/db/models/
"""
import datetime

import django.utils.timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy
from django.contrib.auth.models import User


# Create your models here.
class Club(models.Model):
    """A customer account (tenant). All players, skills and plans belong to exactly one club."""

    TRIALING, ACTIVE, PAST_DUE, CANCELED = "trialing", "active", "past_due", "canceled"
    STATUS_CHOICES = [(s, s) for s in (TRIALING, ACTIVE, PAST_DUE, CANCELED)]

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=django.utils.timezone.now)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=TRIALING)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    # Normalized owner email (lowercase, +tag and Gmail dots removed). Unique, so one free trial per person even
    # under concurrent sign-ups; NULL for clubs created before this existed.
    trial_key = models.CharField(max_length=254, null=True, blank=True, unique=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, default="")
    stripe_subscription_id = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.name

    @property
    def is_entitled(self) -> bool:
        """Whether the club may use the management features right now."""
        now = django.utils.timezone.now()
        if self.status == self.ACTIVE:
            return True
        if self.status == self.TRIALING:
            return bool(self.trial_ends_at and self.trial_ends_at > now)
        # Cancelled/past-due clubs keep access until the period they paid for ends.
        return bool(self.current_period_end and self.current_period_end > now)


class ContactMessage(models.Model):
    """A "contact us" enquiry from the public site (e.g. interest in the full version)."""

    name = models.CharField(max_length=120)
    email = models.EmailField()
    club = models.CharField(max_length=255, blank=True, default="")
    message = models.TextField(max_length=4000)
    locale = models.CharField(max_length=8, blank=True, default="")
    created_at = models.DateTimeField(default=django.utils.timezone.now)
    handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Membership(models.Model):
    OWNER, COACH, VIEWER = "owner", "coach", "viewer"
    ROLE_CHOICES = [(r, r) for r in (OWNER, COACH, VIEWER)]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="membership")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=COACH)

    def __str__(self):
        return f"{self.user} @ {self.club} ({self.role})"


class Invitation(models.Model):
    """Owner-issued invite for another coach to join the club (counts against the seat limit)."""

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="invitations")
    email = models.EmailField()
    role = models.CharField(max_length=16, choices=Membership.ROLE_CHOICES, default=Membership.COACH)
    token = models.CharField(max_length=64, unique=True)
    invited_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="+")
    created_at = models.DateTimeField(default=django.utils.timezone.now)
    accepted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.email} -> {self.club}"


class Category(models.Model):
    """
    Documentation for Category class
    it is a class that refers to Category table in the database.
    it consists of two columns:
        1) Id which is the primary key and it is auto-generated.
        2) name refers to the name of the category
    """
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=255, verbose_name=gettext_lazy('name'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = gettext_lazy('category')
        verbose_name_plural = gettext_lazy('categories')


class Skills(models.Model):
    """
        Documentation for Skills class
        it is a class that refers to Skills table in the database.
        it consists of four columns:
            1) Id which is the primary key and it is auto-generated.
            2) skill_name refers to the name of the skill.
            3) comment refers to a small message that the manager will write it about the skill.
            4) category, it is a ForeignKey for the Category models.
        Read more about [ForeignKey](https://docs.oracle.com/cd/E17952_01/mysql-5.6-en/create-table-foreign-keys.html)
        """
    skill_name = models.CharField(max_length=255, verbose_name=gettext_lazy('skill_name'))
    comment = models.CharField(max_length=255, verbose_name=gettext_lazy('comment'))
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="skills")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=gettext_lazy('category'))

    def __str__(self):
        return self.skill_name

    class Meta:
        verbose_name = gettext_lazy('skill')
        verbose_name_plural = gettext_lazy('skills')


class Player(models.Model):
    """
    Documentation for Player class
        it is a class that refers to Players table in the database.
        it consists of 12 columns:
            1) Id which is the primary key and it is auto-generated.
            2) name refers to the name of the Player.
            3) first_name refers to first name of a player.
            4) address refers to Street, house number of a player.
            5) post_code refers to Post code of a player.
            6) city refers to city of a player.
            7) society refers to Society of a player.
            8) date_of_birth refers to Date of birth of a player.
            9) phone_number refers to phone number of a player.
            10) email_address refers to email address of a player.
            11) image refers to a player profile image.
            12) skills, it is a many to many relation field.Many to many field means that each player has many skills and each skill may be relate to many players.
        You can read more about Many to many relation in database from here: https://docs.oracle.com/cd/B14099_19/web.1012/b15900/relatn014.htm.
    """
    name = models.CharField(max_length=255, verbose_name=gettext_lazy("name"))  # name
    first_name = models.CharField(max_length=255, verbose_name=gettext_lazy("first_name"))  # first name
    address = models.CharField(max_length=255,
                               verbose_name=gettext_lazy("street_house number"))  # Street, house number
    post_code = models.CharField(max_length=255, verbose_name=gettext_lazy("post_code"))  # Post code
    city = models.CharField(max_length=255, verbose_name=gettext_lazy("city"))  # city
    society = models.CharField(max_length=255, verbose_name=gettext_lazy("society"))  # Society
    date_of_birth = models.DateField(auto_now=False, auto_now_add=False,
                                     verbose_name=gettext_lazy("date_of_birth"))  # Date of birth.
    phone_number = models.CharField(default="0", max_length=255,
                                    verbose_name=gettext_lazy("phone_number"))  # phone number
    email_address = models.EmailField(verbose_name=gettext_lazy("email_address"))  # email address.
    image = models.ImageField(null=True, upload_to="images/", default="images/no_image.png",
                              blank=True, verbose_name=gettext_lazy("image"))
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="players")
    skills = models.ManyToManyField(Skills, through='PlayerSkills')

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = gettext_lazy('player')
        verbose_name_plural = gettext_lazy('players')

class PlayerSkills(models.Model):
    """
    Documentation for PlayerSkills class
        it is a class that refers to the relation between Players and skills.
        it consists of 4 columns:
            1) Id which is the primary key and it is auto-generated.
            2) player refers to the name of the Player.
            3) skill refers to first name of the skill.
            4) value refers to evaluation value in range from 1 to 5.
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name=gettext_lazy("player"))
    skill = models.ForeignKey(Skills, on_delete=models.CASCADE, verbose_name=gettext_lazy("skill"))
    value = models.IntegerField(default=0, verbose_name=gettext_lazy("value"),
                                validators=[MinValueValidator(1), MaxValueValidator(5)])
    modified_by = models.CharField(max_length=255)
    modified_at = models.DateTimeField(default=django.utils.timezone.now)

    class Meta:
        verbose_name = gettext_lazy('player skill')
        verbose_name_plural = gettext_lazy('player skills')
        unique_together = ['player', 'skill']


class Plans(models.Model):
    """
    Documentation for Plans class
        it is a class that refers to Plans table in the database.
        it consists of 5 columns:
            1) Id which is the primary key and it is auto-generated.
            2) image refers to the plan image that the manager have draw it before.
            3) created_at refers to date and time when the manager draw this plan.
            4) created_by refers to name of the manager who draws this plan.
            5) comment refers to a small message that the manager will write it about the this plan.
    """
    title = models.CharField(max_length=255, blank=True, default="")
    image = models.ImageField(upload_to="images/", verbose_name=gettext_lazy("image_filed"))
    # Editable state of the tactics board (players, arrows, shapes...) so a plan can be reopened.
    board = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(default=django.utils.timezone.now, verbose_name=gettext_lazy("created_at"))
    created_by = models.CharField(max_length=255, verbose_name=gettext_lazy("created_by"))
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="plans")
    # Set while the plan is shared via a public read-only link.
    share_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
    comment = models.CharField(max_length=255, verbose_name=gettext_lazy("comment"))

    class Meta:
        verbose_name = gettext_lazy('plan')
        verbose_name_plural = gettext_lazy('plans')


