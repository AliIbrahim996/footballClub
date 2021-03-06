from django.urls import path

from . import views
from django.contrib.auth import views as view

urlpatterns = [
    path('', views.player_list, name='players'),
    path('create', views.player_form, name='create'),
    path('<int:p_id>', views.player_delete, name='delete'),
    path('<int:p_id>/', views.player_update, name='update'),
    path('add', views.add_player, name='add'),
    path('tactics', views.tactic, name='tactic'),
    path('plans', views.plans, name='plans'),
    path('evaluation/<int:p_id>', views.evaluate_player, name='evaluation'),
    path('logout', view.LogoutView.as_view(), name='playerLogout'),
    path('save', views.save_plan, name='save'),
    path('search', views.search, name='search'),
    path('evaluation/save', views.save_evaluation, name='save_evaluation'),
]
