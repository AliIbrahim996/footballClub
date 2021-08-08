from django.shortcuts import render
from django.http import HttpResponse
from django.template.context_processors import request

from .models import Player
from django.shortcuts import redirect
from .forms import PlayerValidator
from django.conf import settings
from django.core.files.storage import FileSystemStorage


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
            # to save in  media root directory
            # my_file = request.FILES['image']
            # fs = FileSystemStorage()
            # file_name = fs.save(my_file.name, my_file)
            # print(fs.url(file_name))
            # ************************************
            form.save()
            request.session.clear()
            return redirect('players')
        else:
            print("Invalid inputs")
            print(request.POST)
            request.session['form_errors'] = form.errors
            request.session['data'] = request.POST
            print(form.errors)
            return redirect(player_form)
