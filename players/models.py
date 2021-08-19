import django.utils.timezone
from django.db import models
from django.utils.translation import ugettext_lazy


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name=ugettext_lazy('name'))

    class Meta:
        verbose_name = ugettext_lazy('Category')


class Skills(models.Model):
    skill_name = models.CharField(max_length=255, verbose_name=ugettext_lazy('skill_name'))
    comment = models.CharField(max_length=255, verbose_name=ugettext_lazy('comment'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=ugettext_lazy('category'))

    class Meta:
        verbose_name = ugettext_lazy('Skills')


class Player(models.Model):
    name = models.CharField(max_length=255, verbose_name=ugettext_lazy("name"))  # name
    first_name = models.CharField(max_length=255, verbose_name=ugettext_lazy("first_name"))  # first name
    address = models.CharField(max_length=255,
                               verbose_name=ugettext_lazy("street_house number"))  # Street, house number
    post_code = models.CharField(max_length=255, verbose_name=ugettext_lazy("post_code"))  # Post code
    city = models.CharField(max_length=255, verbose_name=ugettext_lazy("city"))  # city
    society = models.CharField(max_length=255, verbose_name=ugettext_lazy("society"))  # Society
    date_of_birth = models.DateField(auto_now=False, auto_now_add=False,
                                     verbose_name=ugettext_lazy("date_of_birth"))  # Date of birth.
    phone_number = models.CharField(default="0", max_length=255,
                                    verbose_name=ugettext_lazy("phone_number"))  # phone number
    email_address = models.EmailField(verbose_name=ugettext_lazy("email_address"))  # email address.
    image = models.ImageField(null=True, upload_to="images/", default="images/no_image.png",
                              blank=True, verbose_name=ugettext_lazy("image"))
    skills = models.ManyToManyField(Skills, through='PlayerSkills')

    class Meta:
        verbose_name = ugettext_lazy('Player')


class PlayerSkills(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name=ugettext_lazy("player"))
    skill = models.ForeignKey(Skills, on_delete=models.CASCADE, verbose_name=ugettext_lazy("skill"))
    value = models.IntegerField(default=0, verbose_name=ugettext_lazy("value"))

    class Meta:
        verbose_name = ugettext_lazy('Player_Skills')


class Plans(models.Model):
    image = models.ImageField(upload_to="images/", verbose_name=ugettext_lazy("image"))
    created_at = models.DateTimeField(default=django.utils.timezone.now, verbose_name=ugettext_lazy("created_at"))
    created_by = models.CharField(max_length=255, verbose_name=ugettext_lazy("created_by"))
    comment = models.CharField(max_length=255, verbose_name=ugettext_lazy("comment"))

    class Meta:
        verbose_name = ugettext_lazy('Plans')
