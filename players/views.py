from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.

def player_form(request):
    return render(request, "players/player_form.html")


def player_list(request):
    return render(request, "players/player_list.html")


def player_delete(request):
    return HttpResponse("Hello,world")
