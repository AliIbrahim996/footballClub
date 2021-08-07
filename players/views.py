from django.shortcuts import render
from django.http import HttpResponse
from .models import Player
from django.shortcuts import redirect
from .forms import PlayerValidator


# Create your views here.

def player_form(request):
    return render(request, "players/player_form.html")


def player_list(request):
    return render(request, "players/player_list.html")


def player_delete(request):
    return HttpResponse("Hello,world")


def add_player(request):
    if request.method == 'POST':
        form = PlayerValidator(request.POST, request.FILES)
        if form.is_valid():
            player = Player()
            player.name = request.POST.get('name')
            player.vorname = request.POST.get('first_name')
            player.Straße_Hausnummer = request.POST.get('address')
            player.geburtstag = request.POST.get('date_of_birth')
            player.stadt = request.POST.get('city')
            player.telefonnummer = request.POST.get('phone_number')
            player.verein = request.POST.get('society')
            player.postleitzahl = request.POST.get('post_code')
            player.email_adresse = request.POST.get('email')
            player.foto = request.POST.get('image')
            player.save()
            return redirect('players')
        else:
            print("values invalid")
