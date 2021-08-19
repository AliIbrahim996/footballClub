from django.shortcuts import render
# from django.http import JsonResponse
from django.shortcuts import redirect
# from django.core import serializers
# import json
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


# Create your views here.
@login_required
def player_form(request):
    player = PlayerValidator()
    return render(request, "players/player_form.html", {'form': player})


@login_required
def player_list(request):
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
    tactic = PlanForm()
    return render(request, 'plans/tactic.html', {'tactic': tactic})


@login_required
def plans(request):
    """

    :param request:
    :return: plan list page
    """
    try:
        plan = Plans.objects.all()
        users = User.objects.all()
        context = {'plan_list': plan, 'users': users}
        return render(request, 'plans/plan_lists.html', context)
    except Plans.DoesNotExist:
        request.session['data'] = 'No data found'
        return render(request, 'plans/plan_lists.html')


@login_required
def search(request):
    """

    :param request
    :return: result query results after executing query or no data found
    """
    if request.method == "GET":
        try:
            plan = Plans.objects.all()
            users = User.objects.all()
            if '_user' in request.GET:
                plan = plan.filter(created_by=request.GET['_user'])
            if '_start_date' in request.GET and '_end_date' in request.GET:
                plan = plan.filter(created_at__gt=request.GET['_start_date'], created_at__lt=request.GET['_end_date'])
            if '_search_box' in request.GET:
                plan = plan.filter(comment__contains=request.GET['_search_box'])
            context = {'plan_list': plan, 'users': users}
            # print(plan.values())
            #  data = serializers.serialize("json", plan)
            #  return JsonResponse(data, safe=False)
            return render(request, 'plans/plan_lists.html', context)
        except Plans.DoesNotExist:
            request.session['data'] = 'No data found'
            return render(request, 'plans/plan_lists.html')


@login_required
def evaluate_player(request, p_id=0):
    categories = Category.objects.all()
    context = {'categories_list': categories, 'p_id': p_id}

    return render(request, 'players/evaluation_page.html', context)


@login_required
def save_plan(request):
    if request.method == 'POST':
        plan_form = PlanForm(request.POST, request.FILES)
        # print(request.POST)
        # print(request.FILES)
        if plan_form.is_valid():
            plan_form.save()
            return redirect('tactic')
        else:
            request.session['error'] = plan_form.errors
            tactic = plan_form
            return render(request, 'plans/tactic.html', {'tactic': tactic})
    else:
        return render(request, 'plans/tactic.html')
