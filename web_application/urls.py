"""
--------------------------------------List of all urls in the application--------------------------------------
/{lang}/                                web_application.views.home              home
/{lang}/login/                          django.contrib.auth.views.LoginView     login
/{lang}/player/                         players.views.player_list               players
/{lang}/player/<int:p_id>               players.views.player_delete             delete
/{lang}/player/<int:p_id>/              players.views.player_update             update
/{lang}/player/add                      players.views.add_player                add
/{lang}/player/create                   players.views.player_form               create
/{lang}/player/evaluation/<int:p_id>    players.views.evaluate_player           evaluation
/{lang}/player/logout                   django.contrib.auth.views.LogoutView    playerLogout
/{lang}/player/plans                    players.views.plans                     plans
/{lang}/player/save                     players.views.save_plan                 save
/{lang}/player/search                   players.views.search                    search
/{lang}/player/tactics                  players.views.tactic                    tactic
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from . import views as my_views
from django.contrib.auth import views

urlpatterns = i18n_patterns(
    path('', my_views.home, name='home'),
    path('admin/', admin.site.urls, name='admin'),
    path('login/', views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('player/', include('players.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
