from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import PlayerValidator
from .models import Player


# Create your views here.

def player_form(request):
    player = PlayerValidator()
    return render(request, "players/player_form.html", {'form': player})


def player_list(request):
    context = {'player_list': Player.objects.all()}
    return render(request, "players/player_list.html", context)


def player_delete(request, p_id=0):
    return HttpResponse("Hello,world")


def player_update(request, p_id=0):
    if request.method == 'GET':
        player_object = Player.objects.get(pk=p_id)
        form = PlayerValidator(instance=player_object)
        return render(request, "players/player_update.html", {'form': form, 'p_id': p_id})
    elif request.method == 'POST':
        player_object = Player.objects.get(pk=p_id)
        form = PlayerValidator(request.POST, instance=player_object)
        if form.is_valid():
            form.save()
            return redirect('players')
        else:
            player = form
            return render(request, "players/player_update.html", {'form': player})


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
