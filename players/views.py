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
        form = PlayerValidator(request.POST)
        if form.is_valid():
            player = Player()
            player.name = request.POST.get('name')
            player.first_name = request.POST.get('first_name')
            player.address = request.POST.get('address')
            player.date_of_birth = request.POST.get('date_of_birth')
            player.city = request.POST.get('city')
            player.phone_number = request.POST.get('phone_number')
            player.society = request.POST.get('society')
            player.post_code = request.POST.get('post_code')
            player.email_address = request.POST.get('email_address')
            player.image = request.POST.get('image')
            player.save()
            return redirect('players')
        else:
            print("Invalid inputs")
            print(request.POST)
            request.session['form_errors'] = form.errors
            request.session['data'] = request.POST
            print(form.errors)
            return redirect(player_form)
