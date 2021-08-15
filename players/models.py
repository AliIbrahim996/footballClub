from django.db import models


# Create your models here.


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


class Skills(models.Model):
    skillType = models.CharField(max_length=255)
