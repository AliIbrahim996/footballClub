import time

from django.db import models

# Create your models here.
from web_application.settings import MEDIA_ROOT


class Player(models.Model):
    name = models.CharField(max_length=255)  # name
    first_name = models.CharField(max_length=255)  # first name
    address = models.CharField(max_length=255)  # Street, house number
    post_code = models.CharField(max_length=255)  # Post code
    city = models.CharField(max_length=255)  # city
    society = models.CharField(max_length=255)  # Society
    date_of_birth = models.DateField(auto_now=False, auto_now_add=False)  # Date of birth.
    phone_number = models.CharField(default="0", max_length=255)  # phone number
    email_address = models.EmailField()  # email address.
    image = models.ImageField(null=True, upload_to="images/", default="images/no_image.png",
                              blank=True)
