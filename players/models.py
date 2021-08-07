from django.db import models


# Create your models here.
class Player(models.Model):
    name = models.CharField(max_length=255)  # name
    vorname = models.CharField(max_length=255)  # first name
    Straße_Hausnummer = models.CharField(max_length=255)  # Street, house number
    postleitzahl = models.CharField(max_length=255)  # Post code
    stadt = models.CharField(max_length=255)  # city
    verein = models.CharField(max_length=255)  # Society
    geburtstag = models.DateField  # Date of birth.
    telefonnummer = models.IntegerField  # phone number
    email_adresse = models.EmailField  # email address.
    foto = models.ImageField(null=True, upload_to='images/', default='images/no_image.png', blank=True)
