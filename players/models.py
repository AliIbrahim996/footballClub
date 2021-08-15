import django.utils.timezone
from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)


class Skills(models.Model):
    skill_name = models.CharField(max_length=255)
    comment = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Player(models.Model):
    name = models.CharField(max_length=255, verbose_name="name")  # name
    first_name = models.CharField(max_length=255, verbose_name="vorname")  # first name
    address = models.CharField(max_length=255, verbose_name="Straße_Hausnummer")  # Street, house number
    post_code = models.CharField(max_length=255, verbose_name="postleitzahl")  # Post code
    city = models.CharField(max_length=255, verbose_name="stadt")  # city
    society = models.CharField(max_length=255, verbose_name="verein")  # Society
    date_of_birth = models.DateField(auto_now=False, auto_now_add=False, verbose_name="geburtstag")  # Date of birth.
    phone_number = models.CharField(default="0", max_length=255, verbose_name="telefonnummer")  # phone number
    email_address = models.EmailField(verbose_name="emailadresse")  # email address.
    image = models.ImageField(null=True, upload_to="images/", default="images/no_image.png",
                              blank=True)
    skills = models.ManyToManyField(Skills, through='PlayerSkills')


class PlayerSkills(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skills, on_delete=models.CASCADE)
    value = models.IntegerField(default=0)


class Plans(models.Model):
    image = models.ImageField(upload_to="images/")
    created_at = models.DateTimeField(default=django.utils.timezone.now)
    created_by = models.CharField(max_length=255)
