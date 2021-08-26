from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.db.models import TextField
from django.shortcuts import render
# from django.http import JsonResponse
from django.shortcuts import redirect
# from django.core import serializers
# import json
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms import modelformset_factory, inlineformset_factory
from django.core.paginator import Paginator


# Create your views here.
@login_required
def player_form(request):
    """
    A function that render player form.
    :param request: POST request sent from client
    :return: an html page to add a new player
    """
    player = PlayerValidator()
    return render(request, "players/player_form.html", {'form': player})


@login_required
def player_list(request):
    """
    A function that render player list page.
    :param request: POST request sent from client
    :return: an html page with list of all players in the database.
    """
    paginator = Paginator(Player.objects.all(), 12)
    page_number = request.GET.get('page')
    context = {'player_list': paginator.get_page(page_number)}
    return render(request, "players/player_list.html", context)


@login_required
def player_delete(request, p_id=0):
    """
    A function that delete  player information  in database.
    :param request: POST request sent from the client.
    :param p_id: player id that you want to delete.
    :return: player page
    """
    if request.method == 'POST':
        Player.objects.filter(pk=p_id).delete()
    return redirect('players')


@login_required
def player_update(request, p_id=0):
    """
    A function that update  player information  in database.
    :param request: POST request sent from the client with player info.
    :param p_id: player id that you want to update.
    :return: player page
    """
    if request.method == 'GET':
        player_object = Player.objects.get(pk=p_id)
        form = PlayerValidator(instance=player_object)
        return render(request, "players/player_update.html",
                      {'form': form, 'p_id': p_id})
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
    """
    A function that add new player to Player table in database.
    :param request: POST request sent from the client with player info.
    :return: redirect('players') which will open players page, or re-open add new player page in case of any errors.
    """
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
    """
    A function that open Tactic page in order in draw a new one.
    :param request: post request sent from the client.
    :return: list of all tactic available in the database.
    """
    tactic_el = PlanForm()
    return render(request, 'plans/tactic.html', {'tactic': tactic_el})


@login_required
def plans(request):
    """
    A function that open plan list page.
    :param request: post request sent from the client.
    :return: list of all plans available in the database.
    """
    try:
        plans = Plans.objects.all()
        paginator = Paginator(plans, 12)
        page_number = request.GET.get('page')
        users = User.objects.all()
        context = {'plan_list': paginator.get_page(page_number), 'users': users}
        return render(request, 'plans/plan_lists.html', context)
    except Plans.DoesNotExist:
        request.session['data'] = 'No data found'
        return render(request, 'plans/plan_lists.html')


@login_required
def search(request):
    """
    A function that search for plans with specified search parameters.
    :param request: GET request sent from the client with search parameters.
    :return: search results after executing query or no data found.
    """
    if request.method == "GET":
        users = User.objects.all()
        print(request.GET)
        try:
            plan = Plans.objects.all()
            if 'manager' in request.GET:
                plan = plan.filter(created_by=request.GET['manager'])
            if 'start_date' in request.GET and 'end_date' in request.GET:
                plan = plan.filter(created_at__gt=request.GET['start_date'], created_at__lt=request.GET['end_date'])
            if 'search_box' in request.GET:
                plan = plan.filter(comment__contains=request.GET['search_box'])
            paginator = Paginator(plan, 12)
            page_number = request.GET.get('page')
            context = {'plan_list': paginator.get_page(page_number), 'users': users}
            # print(plan.values())
            #  data = serializers.serialize("json", plan)
            #  return JsonResponse(data, safe=False)
            return render(request, 'plans/plan_lists.html', context)
        except Plans.DoesNotExist:
            context = {'users': users}
            request.session['data'] = 'No data found'
            return render(request, 'plans/plan_lists.html', context)


def get_form_set_helper():
    form_set_helper = FormHelper()
    form_set_helper.template = 'bootstrap4/table_inline_formset.html'
    form_set_helper.form_tag = False
    form_set_helper.add_input(Submit('submit', 'Save', css_class='btn btn_submit'))
    form_set_helper.form_method = 'POST'
    return form_set_helper


@login_required
def evaluate_player(request, p_id=0):
    """
    A function that open evaluation page.
    :param request: post request sent from the client.
    :param p_id: refers to the player id that you want to evaluate.
    :return: a query results after executing query or no data found.
    """
    player = Player.objects.get(pk=p_id)
    skills_form_set = inlineformset_factory(Player, PlayerSkills, PlayerSkillsForm, can_delete=False,
                                            formset=PlayerSkillsFormset, extra=0)
    form_set = skills_form_set(instance=player)
    form_set.helper = get_form_set_helper()
    context = {'form_set': form_set, 'p_id': p_id}
    return render(request, 'players/evaluation_page.html', context)


@login_required
def save_evaluation(request):
    if request.method == "POST":
        p_id = request.POST['p_id']
        player = Player.objects.get(pk=p_id)
        skills_form_set = inlineformset_factory(Player, PlayerSkills, PlayerSkillsForm, can_delete=False,
                                                formset=PlayerSkillsFormset, )
        form_set = skills_form_set(request.POST, instance=player)
        if form_set.is_valid():
            form_set.save()
            return redirect('players')
        else:
            form_set.helper = get_form_set_helper()
            context = {'form_set': form_set, 'p_id': p_id}
            return render(request, 'players/evaluation_page.html', context)


@login_required
def save_plan(request):
    """
    A function that save a new plan in the database.
    :param request: post request sent from the client
    :return: result query results after executing query or no data found
    """
    if request.method == 'POST':
        plan_form = PlanForm(request.POST, request.FILES)
        if plan_form.is_valid():
            plan_form.save()
            return redirect('tactic')
        else:
            request.session['error'] = plan_form.errors
            tactic = plan_form
            return render(request, 'plans/tactic.html', {'tactic': tactic})
    else:
        return render(request, 'plans/tactic.html')
