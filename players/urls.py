from django.urls import path

from . import views

urlpatterns = [
    path('', views.player_list, name='players'),
    path('create', views.player_form, name='create'),
    path('<int:p_id>', views.player_delete, name='delete'),
    path('<int:p_id>/', views.player_update, name='update'),
    path('add', views.add_player, name='add'),
    path('tactics', views.tactic, name='tactic')
]
