from django.shortcuts import redirect
from django.shortcuts import render


def home(request):
    return redirect('login')
