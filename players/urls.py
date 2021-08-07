from django.urls import path

from . import views

urlpatterns = [
    path('', views.player_list, name='players'),
    path('create', views.player_form, name='create'),
    path('delete', views.player_delete, name='delete'),
]
