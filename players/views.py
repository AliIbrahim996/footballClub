from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import PlayerValidator


# Create your views here.

def player_form(request):
    player = PlayerValidator()
    return render(request, "players/player_form.html", {'form': player})


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
            return redirect('players')
        else:
            player = form
            return render(request, "players/player_form.html", {'form': player})
    elif request.method == 'GET':
        player = PlayerValidator()
        return render(request, "players/player_form.html", {'form': player})
