from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def player_form(request):
    player = PlayerValidator()
    return render(request, "players/player_form.html", {'form': player})


@login_required
def player_list(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("/admin/")
        else:
            context = {'player_list': Player.objects.all()}
            return render(request, "players/player_list.html", context)


@login_required
def player_delete(request, p_id=0):
    if request.method == 'POST':
        Player.objects.filter(pk=p_id).delete()
    return redirect('players')


@login_required
def player_update(request, p_id=0):
    if request.method == 'GET':
        player_object = Player.objects.get(pk=p_id)
        form = PlayerValidator(instance=player_object)
        return render(request, "players/player_update.html",
                      {'form': form, 'p_id': p_id, 'skills': Skills.objects.all()})
    elif request.method == 'POST':
        player_object = Player.objects.get(pk=p_id)
        form = PlayerValidator(request.POST, instance=player_object)
        if form.is_valid():
            form.save()
            return redirect('players')
        else:
            player = form
            return render(request, "players/player_update.html", {'form': player})


@login_required
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


@login_required
def tactic(request):
    return render(request, 'players/tactic.html')
